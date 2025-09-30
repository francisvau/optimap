/**
 * Capitalizes the first character of a given string.
 *
 * @param str - The input string to capitalize.
 * @returns A new string with the first character converted to uppercase and the rest of the string unchanged.
 */
export function capitalize(str: string) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
