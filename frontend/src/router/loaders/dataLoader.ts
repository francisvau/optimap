import { getBlueprint } from '@/services/mapping/blueprintService';
import { queryClient } from '@/services/client';
import { getOrganizationById } from '@/services/organizationService';
import { LoaderFunctionArgs, redirect } from 'react-router';
import { getJob } from '@/services/mapping/jobService';

/**
 * Loader function for fetching blueprint data based on the provided parameters.
 *
 * @param {LoaderFunctionArgs} args - The arguments object containing route parameters.
 * @param {Record<string, string | undefined>} args.params - The route parameters, including the blueprint ID.
 * @returns {Promise<Response>} A promise that resolves to an HTTP response. If the `blueprint` parameter is missing,
 *                              a 400 Bad Request response is returned with an appropriate error message.
 */
export async function blueprintLoader({ params }: LoaderFunctionArgs): Promise<Response> {
    const blueprintId = parseInt(params.blueprint);

    if (isNaN(blueprintId)) {
        return Response.redirect(
            `/dashboard/blueprints?error=Invalid blueprint ID: ${params.blueprint}`,
        );
    }

    try {
        const blueprint = await queryClient.fetchQuery({
            queryKey: ['blueprint', blueprintId],
            queryFn: async () => await getBlueprint(blueprintId),
        });
        return Response.json(blueprint);
    } catch (error) {
        return Response.redirect(
            `/dashboard/blueprints?error=Failed to load blueprint: ${error.message}`,
        );
    }
}

/**
 * Loads organization data based on the provided route parameters.
 *
 * This function fetches the organization details using the `queryClient`.
 *
 * @param {LoaderFunctionArgs} args - The arguments containing route parameters.
 *
 * @returns {Promise<Response>} A promise that resolves to a JSON response with the
 * organization data or a redirect response in case of an error.
 */
export async function organizationLoader({ params }: LoaderFunctionArgs): Promise<Response> {
    const organizationId = parseInt(params.organizationId);

    if (isNaN(organizationId)) {
        return Response.redirect(
            `/dashboard?error=Invalid organization ID: ${params.organizationId}`,
        );
    }

    try {
        const organization = await queryClient.fetchQuery({
            queryKey: ['organization', organizationId],
            queryFn: () => getOrganizationById(organizationId),
        });
        return Response.json(organization);
    } catch (error) {
        return redirect(`/dashboard?error=Failed to load organization: ${error.message}`);
    }
}

/**
 * Asynchronous loader function to fetch job data based on the provided job ID.
 *
 * This function validates the `jobId` parameter, fetches the job data using a query client,
 * and returns the data as a JSON response. If the `jobId` is invalid or an error occurs
 * during data fetching, it redirects to the jobs dashboard with an appropriate error message.
 *
 * @param {LoaderFunctionArgs} params - An object containing route parameters, including the `jobId`.
 * @returns A `Response` object containing the job data as JSON or a redirection to the jobs dashboard.
 *
 * @throws Redirects to the jobs dashboard with an error message if:
 * - The `jobId` is not a valid number.
 * - The job data could not be fetched due to an error.
 */
export async function jobLoader({ params }: LoaderFunctionArgs): Promise<Response> {
    const jobId = parseInt(params.jobId);

    if (isNaN(jobId)) {
        return Response.redirect(`/dashboard/jobs?error=Invalid job ID: ${params.jobId}`);
    }

    try {
        const job = await queryClient.fetchQuery({
            queryKey: ['job', jobId],
            queryFn: () => getJob(jobId),
        });
        return Response.json(job);
    } catch (error) {
        return Response.redirect(`/dashboard/jobs?error=Failed to load job: ${error.message}`);
    }
}
