"use client";

import ContentListPage from "@/components/content/ContentListPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FEATURED_EVENTS];

export default function FeaturedEventsPage() {
  return <ContentListPage {...config} breadcrumbs={crumbsFor(config)} />;
}
