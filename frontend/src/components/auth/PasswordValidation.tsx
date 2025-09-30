import { JSX } from 'react';
import { Message } from 'primereact/message';

type PasswordValidationMessageProps = {
    feedbackMessages: string[];
};

/**
 * PasswordValidationMessage component
 *
 * This component renders a message displaying the password validation feedback.
 *
 * @param {Object} props - The component props.
 * @param {string[]} props.feedbackMessages - The feedback messages to display.
 *
 * @returns {JSX.Element | null} The rendered PasswordValidationMessage component or null if there are no feedback messages.
 *  */
export function PasswordValidationMessage({
    feedbackMessages,
}: PasswordValidationMessageProps): JSX.Element | null {
    if (feedbackMessages.length === 0) return null;

    return (
        <Message
            severity="warn"
            className="mb-3 w-full"
            style={{
                backgroundColor: '#2D2D2D',
                border: '1px solid #FFD700',
                borderRadius: '8px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                padding: '0',
            }}
            content={
                <div className="p-3">
                    <div className="flex align-items-center mb-3">
                        <i
                            className="pi pi-shield text-yellow-500 mr-2"
                            style={{ fontSize: '1.4rem' }}
                        />
                        <span className="font-bold text-yellow-500" style={{ fontSize: '1.1rem' }}>
                            Your password is too weak!
                        </span>
                    </div>
                    <ul className="m-0 pl-3 list-none">
                        {feedbackMessages.map((msg, index) => (
                            <li
                                key={index}
                                className="text-sm flex align-items-center my-2 text-yellow-300"
                            >
                                <i
                                    className="pi pi-circle-fill mr-2"
                                    style={{ fontSize: '0.5rem', color: '#FFD700' }}
                                />
                                {msg}
                            </li>
                        ))}
                    </ul>
                    <div
                        className="mt-3 pt-3 text-center text-yellow-200"
                        style={{ borderTop: '1px solid rgba(255, 215, 0, 0.3)' }}
                    >
                        <i className="pi pi-info-circle mr-2" />
                        <span className="text-sm">
                            Please create a stronger password to continue
                        </span>
                    </div>
                </div>
            }
        />
    );
}
