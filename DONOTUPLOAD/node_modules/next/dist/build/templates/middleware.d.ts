import '../../server/web/globals';
import type { AdapterOptions } from '../../server/web/adapter';
export default function (opts: Omit<AdapterOptions, 'IncrementalCache' | 'page' | 'handler'>): Promise<import("../../server/web/types").FetchEventResult>;
