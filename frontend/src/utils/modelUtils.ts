import gemini from '@/assets/img/logo/gemini.png';
import groq from '@/assets/img/logo/groq.svg';
import deepseek from '@/assets/img/logo/deepseek.png';

export type BaseModelType = 'gemini' | 'groq' | 'deepseek';

export type ModelMeta = {
    logo: string;
    description: string;
};

export const baseModelOptions: BaseModelType[] = ['gemini', 'groq', 'deepseek'];

export const baseModelMeta: Record<BaseModelType, ModelMeta> = {
    gemini: {
        logo: gemini,
        description: 'The fastest option for quick mapping rule generation.',
    },
    deepseek: {
        logo: deepseek,
        description: 'The most advanced option for complex mapping rules, but slower.',
    },
    groq: {
        logo: groq,
        description: 'A good balance between speed and complexity.',
    },
};
