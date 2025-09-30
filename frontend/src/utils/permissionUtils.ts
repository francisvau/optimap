import { Permissions } from '@/types/models/User';

/**
 Formats a permission string by converting it to a more human-readable format.

 @param {Permissions} permission - The permission string to format.
  It is expected to be in uppercase with words separated by underscores (e.g., "READ_ONLY").
 @returns {string} The formatted permission string with each word capitalized and separated by spaces (e.g., "Read Only").
 */
export function formatPermission(permission: Permissions): string {
    return permission
        .split('_') // split by underscores
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // capitalize each word
        .join(' '); // join with spaces
}
