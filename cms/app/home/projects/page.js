"use client";

import ContentListPage from "@/components/content/ContentListPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_PROJECTS];

export default function HomeProjectsPage() {
  return <ContentListPage {...config} breadcrumbs={crumbsFor(config)} />;
}
