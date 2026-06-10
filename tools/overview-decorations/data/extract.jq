# Decorations overview extractor.
# main = items_*.json ; --slurpfile lang = lowercased lang map.
($lang[0]) as $L
| (.effects | map({key:.effectID, value:.name}) | from_entries) as $E
| { generated: (now|todate),
    items: (
      [ .buildings[]
        | select(.buildingGroundType=="DECO")
        | ($L["deco_\(.type|ascii_downcase)_name"]) as $n
        | select($n != null)
        | { name:$n,
            type:.type,
            might:(.mightValue|tonumber? // 0),
            po:(.decoPoints|tonumber? // 0),
            w:(.width|tonumber? // 1),
            h:(.height|tonumber? // 1),
            effects: (
              (.areaSpecificEffects // "")
              | if . == "" then [] else
                  split(",")
                  | map(
                      (split("&")) as $p
                      | ($E[$p[0]] // "") as $en
                      | { v: ($p[1]|tonumber? // 0),
                          # %-style effects: "boost"-named (but not unboosted*) per GeneralsCamp convention
                          pct: (($en|test("boost";"i")) and (($en|test("unboosted";"i"))|not)),
                          label: ($L["effect_name_\($en|ascii_downcase)"] // (if $en == "" then "Effect \($p[0])" else $en end)) }
                    )
                end
            )
          } ]
      | group_by(.name) | map(max_by(.might))      # one row per deco, strongest variant
      | map(.tiles = (.w * .h)
            | .mpt = (if .tiles>0 then ((.might/.tiles)|floor) else 0 end)
            | .size = "\(.w)x\(.h)")
      | sort_by(-.might)
    ) }
