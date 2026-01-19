import { WorkerRequestHandler } from '../../server/lib/setup-server-worker';
import { NodeRequestHandler } from '../../server/next-server';
export declare function interceptTestApis(): () => void;
export declare function wrapRequestHandlerWorker(handler: WorkerRequestHandler): WorkerRequestHandler;
export declare function wrapRequestHandlerNode(handler: NodeRequestHandler): NodeRequestHandler;
