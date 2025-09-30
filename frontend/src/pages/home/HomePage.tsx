import { JSX } from 'react';
import { AppBar } from '@/layout/navigation/AppBar';
import { AnimatedImage } from '@/components/shared/AnimatedImage';
import { Button } from 'primereact/button';
import { AnimatedBackground } from '@/components/shared/AnimatedBackground';
import { NavLink } from 'react-router';
import illustration from '@/assets/img/illustration/cloud-min.png';
import { useAuth } from '@/hooks/context/AuthProvider/AuthContext';

/**
 * HomePage component renders a simple greeting message.
 *
 * @returns {JSX.Element} A heading element with the text "Hello, world!"
 */
export function HomePage(): JSX.Element {
    const { user } = useAuth();
    return (
        <>
            <AnimatedBackground />
            <div id="page-hero" className="relative">
                <div className="h-full min-h-screen flex flex-column w-12 md:w-10 xl:w-8 mx-auto px-3 pt-5 pb-3">
                    <div className="mb-5">
                        <AppBar />
                    </div>
                    <div className="grid flex-column-reverse lg:flex-row align-items-center flex-0 lg:flex-1">
                        <div className="col-12 lg:col-6">
                            <h1 className="text-4xl lg:text-7xl mt-0">
                                Effortless Data Mapping with AI-Powered Precision
                            </h1>
                            <p className="text-lg">
                                Tired of manual, time-consuming data mapping? Our solution automates
                                the process using AI, making data integration seamless, accurate,
                                and adaptable—no technical expertise required.
                            </p>
                            <NavLink to={user ? '/dashboard' : '/auth/login'}>
                                <Button
                                    className="mt-3"
                                    label="Get Started"
                                    style={{
                                        padding: '1rem 2rem',
                                        fontSize: '1.1rem',
                                    }}
                                    outlined
                                ></Button>
                            </NavLink>
                        </div>
                        <div className="col-12 lg:col-6">
                            <AnimatedImage src={illustration}></AnimatedImage>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default HomePage;
