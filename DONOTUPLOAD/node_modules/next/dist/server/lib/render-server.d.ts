/// <reference types="node" />
import type { RequestHandler } from '../next';
import { PropagateToWorkersField } from './router-utils/types';
export declare function clearModuleContext(target: string): Promise<void> | undefined;
export declare function deleteAppClientCache(): void | undefined;
export declare function deleteCache(filePaths: string[]): void;
export declare function propagateServerField(dir: string, field: PropagateToWorkersField, value: any): Promise<void>;
export declare function initialize(opts: {
    dir: string;
    port: number;
    dev: boolean;
    minimalMode?: boolean;
    hostname?: string;
    workerType: 'router' | 'render';
    isNodeDebugging: boolean;
    keepAliveTimeout?: number;
    serverFields?: any;
    server?: any;
    experimentalTestProxy: boolean;
    _ipcPort?: string;
    _ipcKey?: string;
}): Promise<{
    requestHandler: RequestHandler;
    upgradeHandler: (req: import("http").IncomingMessage, socket: any, head: any) => Promise<void>;
} | undefined>;
