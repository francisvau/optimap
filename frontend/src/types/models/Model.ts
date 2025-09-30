import { BaseModelType } from '@/utils/modelUtils';

export type Model = {
    id: string;
    name: string;
    tailorPrompt: string[];
    baseModel: BaseModelType;
};
