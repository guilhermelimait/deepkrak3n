#!/usr/bin/env node
import '../server/lib/cpu-profile';
import { CliCommand } from '../lib/commands';
declare const nextBuild: CliCommand;
export { nextBuild };
