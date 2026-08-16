import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile, copyFile } from "node:fs/promises";
import { createWriteStream } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import XLSX from "xlsx";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const companies = JSON.parse(await readFile(path.join(root, "challenge/companies.json"), "utf8")).companies;
const basePrompt = await readFile(path.join(root, "agent/forecast-prompt.md"), "utf8");
const schemaPath = path.join(root, "agent/forecast.schema.json");
const researchDir = path.join(root, "research");
const submissionDir = path.join(root, "submission");
const logDir = path.join(root, "logs");
const stamp = new Date().toISOString().replaceAll(":", "-").replace(/\.\d{3}Z$/, "Z");
const logPath = path.join(logDir, `run-${stamp}.jsonl`);

await Promise.all([mkdir(researchDir, { recursive: true }), mkdir(submissionDir, { recursive: true }), mkdir(logDir, { recursive: true })]);
const logStream = createWriteStream(logPath, { flags: "wx" });

function log(event, details = {}) {
  logStream.write(`${JSON.stringify({ timestamp: new Date().toISOString(), event, ...details })}\n`);
}

function taskPrompt(company) {
  return `${basePrompt}\n\n## Assigned company\n\n${JSON.stringify(company, null, 2)}\n`;
}

function runCodex(company) {
  return new Promise((resolve, reject) => {
    const ticker = company.ticker.replace("LSE:", "");
    const outputPath = path.join(researchDir, `${ticker}.json`);
    const args = [
      "exec", "--ephemeral", "--sandbox", "read-only", "--cd", root,
      "--output-schema", schemaPath, "--output-last-message", outputPath, "-"
    ];
    log("company_started", { ticker: company.ticker, outputPath: path.relative(root, outputPath) });
    const child = spawn("codex", args, { cwd: root, stdio: ["pipe", "pipe", "pipe"] });
    child.stdin.end(taskPrompt(company));
    child.stdout.on("data", chunk => log("codex_stdout", { ticker: company.ticker, text: chunk.toString() }));
    child.stderr.on("data", chunk => log("codex_stderr", { ticker: company.ticker, text: chunk.toString() }));
    child.on("error", reject);
    child.on("close", code => {
      if (code === 0) resolve(outputPath);
      else reject(new Error(`Codex failed for ${company.ticker} with exit code ${code}`));
    });
  });
}

function validateForecast(company, result) {
  const errors = [];
  if (result.company !== company.company) errors.push(`company must be ${company.company}`);
  if (result.ticker !== company.ticker) errors.push(`ticker must be ${company.ticker}`);
  if (result.period !== company.period) errors.push(`period must be ${company.period}`);
  const evidenceIds = new Set(result.evidence?.map(item => item.id));
  const metricMap = new Map(result.forecasts?.map(item => [item.metric, item]));
  for (const expected of company.metrics) {
    const forecast = metricMap.get(expected.label);
    if (!forecast) { errors.push(`missing metric ${expected.label}`); continue; }
    if (forecast.units !== expected.units) errors.push(`${expected.label}: units must be ${expected.units}`);
    if (!Number.isFinite(forecast.value)) errors.push(`${expected.label}: value must be finite`);
    if (!(forecast.bear <= forecast.value && forecast.value <= forecast.bull)) errors.push(`${expected.label}: require bear <= value <= bull`);
    for (const id of forecast.evidenceIds ?? []) if (!evidenceIds.has(id)) errors.push(`${expected.label}: unknown evidence id ${id}`);
    if (expected.units === "%" && Math.abs(forecast.value) > 100) errors.push(`${expected.label}: implausible percentage-points value`);
  }
  if (metricMap.size !== company.metrics.length) errors.push("forecast contains unexpected or duplicate metrics");
  if (errors.length) throw new Error(`${company.ticker} validation failed:\n- ${errors.join("\n- ")}`);
}

function writeWorkbook(company, result) {
  const source = path.join(root, "challenge/templates", company.outputFile);
  const destination = path.join(submissionDir, company.outputFile);
  return copyFile(source, destination).then(() => {
    const workbook = XLSX.readFile(destination, { cellStyles: true });
    const sheet = workbook.Sheets.Summary;
    const values = new Map(result.forecasts.map(item => [item.metric, item.value]));
    for (let row = 7; row <= 9; row += 1) {
      const label = sheet[`A${row}`]?.v;
      sheet[`C${row}`] = { ...(sheet[`C${row}`] ?? {}), t: "n", v: values.get(label) };
    }
    XLSX.writeFile(workbook, destination, { bookType: "xlsx", cellStyles: true });
    return destination;
  });
}

async function main() {
  log("run_started", { command: "npm run forecast", companies: companies.map(c => c.ticker) });
  const outputPaths = await Promise.all(companies.map(runCodex));
  for (let index = 0; index < companies.length; index += 1) {
    const company = companies[index];
    const result = JSON.parse(await readFile(outputPaths[index], "utf8"));
    validateForecast(company, result);
    const workbook = await writeWorkbook(company, result);
    log("company_completed", { ticker: company.ticker, workbook: path.relative(root, workbook), forecasts: result.forecasts.map(({ metric, units, value }) => ({ metric, units, value })) });
  }
  log("run_completed", { workbooks: companies.map(c => `submission/${c.outputFile}`) });
  logStream.end();
  console.log(`Forecast run complete. Log: ${path.relative(root, logPath)}`);
}

main().catch(error => {
  log("run_failed", { error: error.stack ?? String(error) });
  logStream.end();
  console.error(error.message);
  process.exitCode = 1;
});
