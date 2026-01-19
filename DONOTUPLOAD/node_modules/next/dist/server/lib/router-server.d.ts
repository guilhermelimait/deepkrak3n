import type { WorkerRequestHandler, WorkerUpgradeHandler } from './setup-server-worker';
import '../node-polyfill-fetch';
import '../node-environment';
import '../require-hook';
export type RenderWorker = Pick<typeof import('./render-server'), 'initialize' | 'deleteCache' | 'clearModuleContext' | 'deleteAppClientCache' | 'propagateServerField'>;
export interface RenderWorkers {
    app?: RenderWorker;
    pages?: RenderWorker;
}
export declare function initialize(opts: {
    dir: string;
    port: number;
    dev: boolean;
    server?: import('http').Server;
    minimalMode?: boolean;
    hostname?: string;
    workerType: 'router' | 'render';
    isNodeDebugging: boolean;
    keepAliveTimeout?: number;
    customServer?: boolean;
    experimentalTestProxy?: boolean;
}): Promise<[WorkerRequestHandler, WorkerUpgradeHandler]>;
