import { useEffect, useRef, useState } from "react";

export type ScrollSyncedInsightTab = {
  id: string;
  label: string;
  meta?: string;
};

type ScrollSyncedInsightTabsProps = {
  ariaLabel: string;
  tabs: ScrollSyncedInsightTab[];
};

export function ScrollSyncedInsightTabs({
  ariaLabel,
  tabs,
}: ScrollSyncedInsightTabsProps) {
  const [activeId, setActiveId] = useState(tabs[0]?.id ?? "");
  const visibilityById = useRef(new Map<string, number>());

  useEffect(() => {
    visibilityById.current.clear();

    if (tabs.length === 0) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const sectionId = entry.target.id;
          visibilityById.current.set(
            sectionId,
            entry.isIntersecting ? entry.intersectionRatio : 0,
          );
        }

        const mostVisible = tabs
          .map((tab) => ({
            id: tab.id,
            ratio: visibilityById.current.get(tab.id) ?? 0,
          }))
          .sort((first, second) => second.ratio - first.ratio)[0];

        if (mostVisible && mostVisible.ratio > 0) {
          setActiveId(mostVisible.id);
        }
      },
      {
        rootMargin: "-24% 0px -56% 0px",
        threshold: [0, 0.15, 0.35, 0.55, 0.75],
      },
    );

    for (const tab of tabs) {
      const section = document.getElementById(tab.id);
      if (section) {
        observer.observe(section);
      }
    }

    return () => {
      observer.disconnect();
    };
  }, [tabs]);

  function handleTabClick(tabId: string) {
    const section = document.getElementById(tabId);
    if (!section) {
      return;
    }

    setActiveId(tabId);
    section.scrollIntoView({
      behavior: prefersReducedMotion() ? "auto" : "smooth",
      block: "start",
    });
  }

  return (
    <nav aria-label={ariaLabel} className="scroll-sync-tabs">
      <ul className="scroll-sync-tabs-track">
        {tabs.map((tab) => {
          const isActive = tab.id === activeId;

          return (
            <li key={tab.id}>
              <button
                aria-current={isActive ? "location" : undefined}
                className={`scroll-sync-tab-button${isActive ? " active" : ""}`}
                onClick={() => handleTabClick(tab.id)}
                type="button"
              >
                {tab.meta ? <span>{tab.meta}</span> : null}
                <strong>{tab.label}</strong>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
