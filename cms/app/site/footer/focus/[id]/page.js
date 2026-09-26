"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_FOCUS];

export default function EditFooterFocusPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit recent focus item"
      description="Update a Footer Recent Focus item."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
