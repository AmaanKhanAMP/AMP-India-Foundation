"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.UPCOMING_EVENTS];

export default function NewUpcomingEventPage() {
  return (
    <ContentFormPage
      {...config}
      title="New upcoming event"
      description="Add an event to the Events page grid."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
