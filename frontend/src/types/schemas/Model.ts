import { BaseModelType } from '@/utils/modelUtils';

export type ModelRequest = {
    name?: string;
    tailorPrompt?: string[];
    baseModel?: BaseModelType;
};
