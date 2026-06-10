# Equipment overview extractor.
# main = items_*.json ; --slurpfile lang = lowercased lang map.
#
# NOTE: IDs inside equipments.effects are equipmentEffectIDs and must be
# chained through equipment_effects to the real effectID. Legacy gear has the
# same ID in both tables (which hides this); all newer gear (Rift sets etc.)
# diverges completely and resolves to nonsense without the chain.
($lang[0]) as $L
| (INDEX(.effects[]; .effectID))                            as $EF
| (INDEX(.equipment_effects[]; .equipmentEffectID))         as $EQF
| (INDEX(.units[]; (.wodID|tostring)))                      as $U
| (INDEX(.equipment_slots[]; .slotID))                      as $SL
| (INDEX(.equipment_wearers[]; .wearerID))                  as $WR
| def L($k): $L[($k|ascii_downcase)];
def cap($s): (($s // "") | if .=="" then "" else (.[0:1]|ascii_upcase) + .[1:] end);
def unitName($wod): (L("\($U[$wod].type)_name") // ("unit " + $wod));
def effText($e):                                  # "57&33" -> "+33% ..."
    ($e|split("&")) as $p
    | (($EQF[$p[0]].effectID) // $p[0]) as $rid   # chain to the real effectID
    | ($EF[$rid].name) as $nm
    | if $nm == null then empty
      else
        (L("equip_effect_description_\($nm)") // $nm) as $tpl
        | ($p[1] // "") as $val
        # unit-targeted values: "<unitWodID>+<count>" with {0}=count {1}=unit
        | (if ($tpl|contains("{1}")) and ($val|test("^[0-9]+\\+[0-9]+$"))
           then ($val|split("+")) as $uv
                | ($tpl | gsub("\\{0\\}"; $uv[1]) | gsub("\\{1\\}"; unitName($uv[0])))
           else ($tpl | gsub("\\{0\\}"; $val))
           end)
        | gsub("\\s*\\{\\d\\}"; "") | gsub("\\+\\-"; "-") | gsub("\\-\\-"; "-")
      end;
{ generated: (now|todate),
  items: (
    [ .equipments[]
      | (L("equipment_unique_\(.equipmentID)") // L("hero_unique_\(.equipmentID)")) as $n
      | select($n != null and ((.mightValue|tonumber? // 0) > 0))
      | { id: .equipmentID,
          reuseId: .reuseAssetOfEquipmentID,
          name: $n,
          slot: cap($SL[.slotID].name),
          set: (L("equipment_set_\(.setID)") // ""),
          wearer: cap($WR[.wearerID].name),
          might: (.mightValue|tonumber? // 0),
          effects: ((.effects // "") | if . == "" then [] else (split(",") | map(effText(.))) end) } ]
    | sort_by(-.might) ) }
