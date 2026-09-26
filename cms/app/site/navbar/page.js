"use client";

import ContentListPage from "@/components/content/ContentListPage";
import NavbarLogoPanel from "@/components/layout/NavbarLogoPanel";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.NAVBAR_ITEMS];

export default function NavbarPage() {
  return (
    <ContentListPage
      {...config}
      breadcrumbs={crumbsFor(config)}
      headerExtra={<NavbarLogoPanel />}
    />
  );
}
