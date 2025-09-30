import { FormProps } from '@/types/Form';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { JSX, useState } from 'react';
import { ModelRequest } from '@/types/schemas/Model';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { baseModelMeta, baseModelOptions, BaseModelType } from '@/utils/modelUtils';

export type ModelFormProps = FormProps<ModelRequest>;

/**
 * A form component for creating or editing a model.
 *
 * @param {ModelFormProps} props - The properties for the ModelForm component.
 *
 * @returns {JSX.Element} The rendered ModelForm component.
 */
export function ModelForm({ isLoading, error, onSubmit, initial }: ModelFormProps): JSX.Element {
    const [form, setForm] = useState<ModelRequest>({
        name: initial?.name ?? '',
        baseModel: initial?.baseModel ?? 'gemini',
        tailorPrompt: initial?.tailorPrompt ?? [],
    });

    const [prompt, setPrompt] = useState<string>(initial?.tailorPrompt.join('\n') ?? '');

    const baseModelItemTemplate = (option: BaseModelType) => {
        return (
            <div className="flex align-items-center gap-2">
                <img
                    src={baseModelMeta[option].logo}
                    style={{ height: '1.5rem', width: '1.5rem', objectFit: 'contain' }}
                />
                <span className="w-5rem">{option}</span>
                <span className="text-300">{baseModelMeta[option].description}</span>
            </div>
        );
    };

    const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        setPrompt(value);
        setForm((prev) => ({
            ...prev,
            tailorPrompt: value.split('\n').filter((line) => line.trim() !== ''),
        }));
    };

    return (
        <>
            {error && <Message severity="error" text={error} className="mb-4 w-full text-center" />}

            <form action={() => void onSubmit(form)}>
                <div className="formgrid grid">
                    <div className="field col-12">
                        <label htmlFor="name">Model Name</label>
                        <InputText
                            id="name"
                            name="name"
                            placeholder="Model Name"
                            value={form.name}
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                            required
                        ></InputText>
                    </div>
                    <div className="field col-12">
                        <label htmlFor="baseModel">Base Model</label>
                        <Dropdown
                            options={baseModelOptions}
                            value={form.baseModel}
                            onChange={(e) => setForm({ ...form, baseModel: e.value })}
                            itemTemplate={baseModelItemTemplate}
                            valueTemplate={baseModelItemTemplate}
                        ></Dropdown>
                    </div>
                    <div className="field col-12">
                        <label htmlFor="prompt">Tailor Prompt</label>
                        <InputTextarea
                            placeholder="The tailor prompt is a set of instructions that guides the model's behavior. Use it to specify important context that the model should consider when generating JSONata mapping rules."
                            value={prompt}
                            onChange={handlePromptChange}
                            rows={5}
                        ></InputTextarea>
                    </div>
                    <div className="col-12 mt-3 mb-3">
                        <Button className="w-full" label="Submit" loading={isLoading}></Button>
                    </div>
                </div>
            </form>
        </>
    );
}
