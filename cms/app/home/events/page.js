"use client";

import ContentListPage from "@/components/content/ContentListPage";
import SectionVisibilityPanel from "@/components/content/SectionVisibilityPanel";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_EVENTS];

export default function HomeEventsPage() {
  return (
    <ContentListPage
      {...config}
      breadcrumbs={crumbsFor(config)}
      headerExtra={
        <SectionVisibilityPanel
          sectionName="home_events"
          sectionLabel="Home Upcoming Events"
        />
      }
    />
  );
}
