#!/usr/bin/env node
import '../server/lib/cpu-profile';
import { CliCommand } from '../lib/commands';
declare const nextDev: CliCommand;
export { nextDev };
