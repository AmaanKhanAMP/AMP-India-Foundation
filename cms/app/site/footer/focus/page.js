"use client";

import ContentListPage from "@/components/content/ContentListPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_FOCUS];

export default function FooterFocusPage() {
  return <ContentListPage {...config} breadcrumbs={crumbsFor(config)} />;
}
