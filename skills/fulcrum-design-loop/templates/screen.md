# Template - `.fulcrum/design/screens/<SID>.md`

One file per screen, written by `fulcrum-capturer`. Limits: <= 150 lines, anatomy <=
80 lines, <= 6 top-level regions. Attribute vocabulary, the four-part mapping and a
worked example: `../references/design-spec-format.md`, heading "screens/<SID>.md".
Never sent to Mentor whole: a driver brief carries one region's subtree per turn.

---

<!-- fulcrum-schema: design-screen v1 -->
# \<SID\> \<Name\> - archetype: \<archetype\> - reference: reference/\<SID\>.\<ext\>
Layout: \<LayoutBlock\>   Access: \<policy\> (\<D-NNN\>)

## Anatomy

```
<LayoutBlock>
  {/* R1 <region name> */} <Block class="<class>" bind="<Entity.Attribute>"> ... </Block>
  {/* R2 <region name> */} ...
</LayoutBlock>
```

## Regions

- R1 \<name\>: \<blocks\>; \<construct: chart | repeater | form | overlay | none\>
- R2 ...

## Icons

- \<region/location\> -> \<semantic name\> -> \<tenant glyph, set at gate | probe\>
- count = \<N\>

## Interactions

- \<node\> -> navigate:\<SID\> | action:\<plain words\>
- \<node\> static

## Acceptance

- F-\<SID\>-01 \<instrument\>: \<observable outcome\>
- F-\<SID\>-02 ...
