"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.UPCOMING_EVENTS];

export default function EditUpcomingEventPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit upcoming event"
      description="Update upcoming event details."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
