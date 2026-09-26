"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_EVENTS];

export default function EditHomeEventPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit home event"
      description="Update homepage event details."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
