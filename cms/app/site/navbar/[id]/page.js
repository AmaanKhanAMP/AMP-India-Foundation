"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.NAVBAR_ITEMS];

export default function EditNavbarItemPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit navbar item"
      description="Update a navigation link or dropdown item."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
