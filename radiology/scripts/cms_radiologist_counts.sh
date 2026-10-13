#!/usr/bin/env bash
# Count NPIs by provider type in CMS "Medicare Physician & Other Practitioners - by Provider"
# (one dataset per data year, 2013-2024) via the data.cms.gov stats endpoint.
# Only counts are saved (no provider-level records).
# Usage (from worktree root): bash projects/radiology/scripts/cms_radiologist_counts.sh
OUT=projects/radiology/data/raw/imaging/cms_mupphy_provider_type_counts.csv
echo "data_year,provider_type,found_rows,total_rows,dataset_api" > $OUT
while read yr id; do
  for t in "Diagnostic Radiology" "Interventional Radiology" "Nuclear Medicine" "Radiation Oncology"; do
    url="https://data.cms.gov/data-api/v1/dataset/$id/data/stats"
    r=$(curl -s -G "$url" --data-urlencode "filter[Rndrng_Prvdr_Type]=$t")
    f=$(echo "$r" | sed -E 's/.*"found_rows":([0-9]+).*/\1/'); a=$(echo "$r" | sed -E 's/.*"total_rows":([0-9]+).*/\1/')
    echo "$yr,$t,$f,$a,$url" >> $OUT
    sleep 0.5
  done
done <<'IDS'
2013 483a68df-26a9-42a5-a24c-7458e5374f61
2014 100d9e00-03cd-4105-9f58-27f9bf9ab773
2015 fb870c06-27f2-4e15-b556-1731d794bb5b
2016 2691839a-99fb-45a1-9bd9-86905ba975cc
2017 44ea2789-993f-4d55-ac44-ed7f160b58fa
2018 900850df-c9a9-47ce-a9e0-d0ceae5a811f
2019 6a53afe5-1cbc-4b33-9dc8-926ee532dc66
2020 29d799aa-c660-44fe-a51a-72c4b3e661ac
2021 44e0a489-666c-4ea4-a1a2-360b6cdc19db
2022 21555c17-ec1b-4e74-b2c6-925c6cbb3147
2023 8ba584c6-a43a-4b0b-a35a-eb9a59e3a571
2024 8889d81e-2ee7-448f-8713-f071038289b5
IDS
cat $OUT
