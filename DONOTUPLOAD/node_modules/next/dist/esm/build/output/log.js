import chalk from "../../lib/chalk";
export const prefixes = {
    wait: chalk.white(chalk.bold("○")),
    error: chalk.red(chalk.bold("X")),
    warn: chalk.yellow(chalk.bold("⚠")),
    ready: chalk.bold("▲"),
    info: chalk.white(chalk.bold(" ")),
    event: chalk.green(chalk.bold("✓")),
    trace: chalk.magenta(chalk.bold("\xbb"))
};
const LOGGING_METHOD = {
    log: "log",
    warn: "warn",
    error: "error"
};
function prefixedLog(prefixType, ...message) {
    if ((message[0] === "" || message[0] === undefined) && message.length === 1) {
        message.shift();
    }
    const consoleMethod = prefixType in LOGGING_METHOD ? LOGGING_METHOD[prefixType] : "log";
    const prefix = prefixes[prefixType];
    // If there's no message, don't print the prefix but a new line
    if (message.length === 0) {
        console[consoleMethod]("");
    } else {
        console[consoleMethod](" " + prefix, ...message);
    }
}
export function bootstrap(...message) {
    console.log(" ", ...message);
}
export function wait(...message) {
    prefixedLog("wait", ...message);
}
export function error(...message) {
    prefixedLog("error", ...message);
}
export function warn(...message) {
    prefixedLog("warn", ...message);
}
export function ready(...message) {
    prefixedLog("ready", ...message);
}
export function info(...message) {
    prefixedLog("info", ...message);
}
export function event(...message) {
    prefixedLog("event", ...message);
}
export function trace(...message) {
    prefixedLog("trace", ...message);
}
const warnOnceMessages = new Set();
export function warnOnce(...message) {
    if (!warnOnceMessages.has(message[0])) {
        warnOnceMessages.add(message.join(" "));
        warn(...message);
    }
}

//# sourceMappingURL=log.js.map