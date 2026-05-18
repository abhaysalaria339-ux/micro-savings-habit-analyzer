import { ComponentType, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import { AdvancedPage } from "./AdvancedPage";
import { BudgetsPage } from "./BudgetsPage";
import { DashboardPage } from "./DashboardPage";
import { ExpensesPage } from "./ExpensesPage";
import { GoalsPage } from "./GoalsPage";
import { InsightsPage } from "./InsightsPage";
import { MorePage } from "./MorePage";
import { SimulatorPage } from "./SimulatorPage";
import { workspaceSectionChangeEvent, workspaceSectionConfig } from "./workspaceConfig";

type WorkspaceSection = {
  Component: ComponentType;
  id: string;
  label: string;
};

const componentBySectionId: Record<string, ComponentType> = {
  "workspace-dashboard": DashboardPage,
  "workspace-expenses": ExpensesPage,
  "workspace-goals": GoalsPage,
  "workspace-budgets": BudgetsPage,
  "workspace-insights": InsightsPage,
  "workspace-advanced": AdvancedPage,
  "workspace-simulator": SimulatorPage,
  "workspace-more": MorePage,
};

const workspaceSections: WorkspaceSection[] = workspaceSectionConfig.map((section) => ({
  ...section,
  Component: componentBySectionId[section.id],
}));

export function WorkspacePage() {
  const location = useLocation();
  const [activeSectionId, setActiveSectionId] = useState(workspaceSections[0].id);

  const sectionIds = useMemo(
    () => workspaceSections.map((section) => section.id),
    [],
  );

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((first, second) => second.intersectionRatio - first.intersectionRatio)[0];

        if (!visibleEntry) {
          return;
        }

        const nextSectionId = visibleEntry.target.id;
        setActiveSectionId(nextSectionId);
        window.dispatchEvent(
          new CustomEvent(workspaceSectionChangeEvent, {
            detail: nextSectionId,
          }),
        );
      },
      {
        rootMargin: "-28% 0px -52% 0px",
        threshold: [0.12, 0.25, 0.45, 0.65],
      },
    );

    for (const sectionId of sectionIds) {
      const section = document.getElementById(sectionId);
      if (section) {
        observer.observe(section);
      }
    }

    return () => {
      observer.disconnect();
    };
  }, [sectionIds]);

  useEffect(() => {
    if (!location.hash) {
      return;
    }

    const section = document.getElementById(location.hash.slice(1));
    if (!section) {
      return;
    }

    window.requestAnimationFrame(() => {
      section.scrollIntoView({
        behavior: prefersReducedMotion() ? "auto" : "smooth",
        block: "start",
      });
    });
  }, [location.hash]);

  return (
    <div className="continuous-workspace" aria-label="Continuous finance workspace">
      {workspaceSections.map(({ Component, id, label }) => (
        <section
          aria-label={label}
          className={`workspace-page-section${activeSectionId === id ? " active" : ""}`}
          id={id}
          key={id}
        >
          <Component />
        </section>
      ))}
    </div>
  );
}

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
