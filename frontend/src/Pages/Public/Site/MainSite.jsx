import AuroraBackground from './AuroraBackground';
import MenuSitePublic from '../../../Components/Utils/MenuSitePublic/MenuSitePublic';
import HeroSection from './Sections/HeroSection/HeroSection';
import AboutSection from './Sections/AboutSection/AboutSection';
import ServicesSection from './Sections/ServicesSection/ServicesSection';
import InfrastructureSection from './Sections/InfrastructureSection/InfrastructureSection';
import FooterSection from './Sections/FooterSection/FooterSection';
import style from './MainSite.module.css';

export default function MainSite() {
    return (
        <AuroraBackground>
            <MenuSitePublic />
            <main className={style.mainContent}>
                <HeroSection />
                <AboutSection />
                <ServicesSection />
                <InfrastructureSection />
                <FooterSection />
            </main>
        </AuroraBackground>
    );
}