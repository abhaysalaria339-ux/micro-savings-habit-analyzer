import {
  ComponentType,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
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
  const activeSectionRef = useRef(workspaceSections[0].id);

  const sectionIds = useMemo(
    () => workspaceSections.map((section) => section.id),
    [],
  );

  const publishActiveSection = useCallback((sectionId: string) => {
    if (activeSectionRef.current === sectionId) {
      return;
    }

    activeSectionRef.current = sectionId;
    setActiveSectionId(sectionId);
    window.dispatchEvent(
      new CustomEvent(workspaceSectionChangeEvent, {
        detail: sectionId,
      }),
    );
  }, []);

  useEffect(() => {
    let animationFrameId: number | null = null;

    function updateActiveSection() {
      animationFrameId = null;

      const anchorY = Math.min(window.innerHeight * 0.36, 280);
      let nextSectionId = activeSectionRef.current;
      let bestDistance = Number.POSITIVE_INFINITY;

      for (const sectionId of sectionIds) {
        const section = document.getElementById(sectionId);
        if (!section) {
          continue;
        }

        const rect = section.getBoundingClientRect();
        const isAnchorInsideSection = rect.top <= anchorY && rect.bottom >= anchorY;
        const distance = isAnchorInsideSection
          ? 0
          : Math.min(Math.abs(rect.top - anchorY), Math.abs(rect.bottom - anchorY));

        if (distance < bestDistance) {
          bestDistance = distance;
          nextSectionId = sectionId;
        }
      }

      publishActiveSection(nextSectionId);
    }

    function scheduleActiveSectionUpdate() {
      if (animationFrameId !== null) {
        return;
      }

      animationFrameId = window.requestAnimationFrame(updateActiveSection);
    }

    scheduleActiveSectionUpdate();
    window.addEventListener("scroll", scheduleActiveSectionUpdate, { passive: true });
    window.addEventListener("resize", scheduleActiveSectionUpdate);

    return () => {
      if (animationFrameId !== null) {
        window.cancelAnimationFrame(animationFrameId);
      }

      window.removeEventListener("scroll", scheduleActiveSectionUpdate);
      window.removeEventListener("resize", scheduleActiveSectionUpdate);
    };
  }, [publishActiveSection, sectionIds]);

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
      publishActiveSection(section.id);
    });
  }, [location.hash, publishActiveSection]);

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
