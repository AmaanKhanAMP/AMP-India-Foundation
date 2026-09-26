"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_LINKS];

export default function EditFooterLinkPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit useful link"
      description="Update a Footer Useful Links item."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
