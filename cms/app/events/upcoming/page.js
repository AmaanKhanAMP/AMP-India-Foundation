"use client";

import ContentListPage from "@/components/content/ContentListPage";
import SectionVisibilityPanel from "@/components/content/SectionVisibilityPanel";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.UPCOMING_EVENTS];

export default function UpcomingEventsPage() {
  return (
    <ContentListPage
      {...config}
      breadcrumbs={crumbsFor(config)}
      headerExtra={
        <SectionVisibilityPanel
          sectionName="upcoming_events"
          sectionLabel="Upcoming Events"
        />
      }
    />
  );
}
