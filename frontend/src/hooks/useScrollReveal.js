import { useEffect, useRef } from 'react';

/**
 * Hook to trigger animations when elements enter the viewport.
 * Adds a 'reveal' class to the element when it's visible.
 */
export const useScrollReveal = (options = {}) => {
    const sectionRef = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    // Once revealed, we can stop observing if we want it to stay
                    if (!options.repeat) {
                        observer.unobserve(entry.target);
                    }
                } else if (options.repeat) {
                    entry.target.classList.remove('revealed');
                }
            });
        }, {
            threshold: options.threshold || 0.1,
            rootMargin: options.rootMargin || '0px',
        });

        const currentRef = sectionRef.current;
        if (currentRef) {
            // Observe children with 'reveal' class or the ref itself
            const elementsToObserve = currentRef.querySelectorAll('.reveal');
            if (elementsToObserve.length > 0) {
                elementsToObserve.forEach(el => observer.observe(el));
            } else {
                observer.observe(currentRef);
            }
        }

        return () => {
            if (currentRef) {
                const elementsToObserve = currentRef.querySelectorAll('.reveal');
                if (elementsToObserve.length > 0) {
                    elementsToObserve.forEach(el => observer.unobserve(el));
                } else {
                    observer.unobserve(currentRef);
                }
            }
        };
    }, [options.repeat, options.threshold, options.rootMargin]);

    return sectionRef;
};
