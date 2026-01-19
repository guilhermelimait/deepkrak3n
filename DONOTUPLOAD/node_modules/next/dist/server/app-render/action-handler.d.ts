/// <reference types="node" />
import type { IncomingMessage, ServerResponse } from 'http';
import type { SizeLimit } from '../../../types';
import RenderResult from '../render-result';
import { StaticGenerationStore } from '../../client/components/static-generation-async-storage.external';
import { ActionResult } from './types';
import { RequestStore } from '../../client/components/request-async-storage.external';
export declare function handleAction({ req, res, ComponentMod, page, serverActionsManifest, generateFlight, staticGenerationStore, requestStore, serverActionsBodySizeLimit, }: {
    req: IncomingMessage;
    res: ServerResponse;
    ComponentMod: any;
    page: string;
    serverActionsManifest: any;
    generateFlight: (options: {
        actionResult: ActionResult;
        skipFlight: boolean;
        asNotFound?: boolean;
    }) => Promise<RenderResult>;
    staticGenerationStore: StaticGenerationStore;
    requestStore: RequestStore;
    serverActionsBodySizeLimit?: SizeLimit;
}): Promise<undefined | RenderResult | 'not-found'>;
