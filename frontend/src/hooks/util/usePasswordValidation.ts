import { useState } from 'react';

/**
 * usePasswordValidation hook
 *
 * This hook provides a function to validate a password and returns feedback messages.
 *
 * @returns {Object} The feedback messages and a function to validate a password.
 */
export function usePasswordValidation(): {
    feedbackMessages: string[];
    validatePassword: (password: string) => void;
} {
    const [feedbackMessages, setFeedbackMessages] = useState<string[]>([]);

    const validatePassword = (password: string) => {
        const messages: string[] = [];

        if (password.length < 8) messages.push('At least 8 characters');
        if (!/[A-Z]/.test(password)) messages.push('At least one uppercase letter');
        if (!/[0-9]/.test(password)) messages.push('At least one number');
        if (!/[^A-Za-z0-9]/.test(password)) messages.push('At least one special character');

        setFeedbackMessages(messages);
    };

    return { feedbackMessages, validatePassword };
}
