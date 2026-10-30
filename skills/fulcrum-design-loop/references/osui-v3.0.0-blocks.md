# OutSystems UI v3.0.0 - block index

Condensed extract of OutSystems UI, tag `v3.0.0`, taken 2026-10-30. BSD-3-Clause, Copyright (c) 2023, OutSystems; see THIRD-PARTY-NOTICE.md. Not endorsed by OutSystems. Generated once by a maintainer; nothing runs at install.
Library facts are `[SCHEMA]`: the vendor describing one library version, not a tenant. Before relying on a row, compare the tag with the tenant's version: `block-map.md`, heading "OutSystems UI library reference".

Source: `docs-ai/osui.blocks.json` at the tag, ODC module version `13.1421.9.60000`. 85 public blocks; the `Private` flow is left out. A key is `<flow>/<name>`, a lookup into this library. How Mentor names a block is `[UNVERIFIED]`: say the plain name in a prompt.

Read a line as `key: Param:Type=default` (`*` mandatory; no default means the type's own; enum defaults drop the `Entities.<Enum>.` prefix) `| slots`. Every block also takes `ExtendedClass:Text`, except `Adaptive/DisplayOnDevice`, `Adaptive/MasterDetail`, `Interaction/Animate`, `Utilities/MouseEvents`, `Utilities/PasswordPolicy`, `Utilities/SwipeEvents`, `Utilities/TouchEvents`. Not listed here at all: layouts, Modal, Popover, Button, Link, Input, Switch, RadioGroup, TextArea, Checkbox, TableRecords, List, charts, Map, the Icon widget (`block-map.md`).

## Adaptive

- `Adaptive/Columns2`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/Columns3`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/Columns4`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/Columns5`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/Columns6`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/ColumnsMediumLeft`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/ColumnsMediumRight`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/ColumnsSmallLeft`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/ColumnsSmallRight`: GutterSize:GutterSize=Base, TabletBehavior:BreakColumns=None, PhoneBehavior:BreakColumns=None
- `Adaptive/DisplayOnDevice`
- `Adaptive/Gallery`: RowItemsDesktop:Integer=4, RowItemsTablet:Integer=3, RowItemsPhone:Integer=1, ItemsGap:Space=Base
- `Adaptive/MasterDetail`: LeftPercentage:Decimal=50, OpenedOnPhone:Boolean=False, Height:Text

## Advanced

- `Advanced/DropdownServerSide`: AllowMultipleSelection:Boolean=False, IsDisabled:Boolean=False
- `Advanced/DropdownServerSideItem`: ItemId*:Text, IsSelected:Boolean=False

## Content

- `Content/Accordion`: MultipleItems:Boolean=False
- `Content/AccordionItem`: StartsExpanded:Boolean=False, Icon:AccordionIconType=Caret, IconPosition:AccordionIconPosition=Right, IsDisabled:Boolean=False
- `Content/Alert`: AlertType:Alert=Info
- `Content/BlankSlate`: FullHeight:Boolean=True
- `Content/Card`: UsePadding:Boolean=True
- `Content/CardBackground`: Color:Color=Transparent, MinHeight:Integer=0
- `Content/CardItem`
- `Content/CardSectioned`: UsePadding:Boolean=True, IsVertical:Boolean=True, ImagePadding:Boolean=True
- `Content/ChatMessage`: DisplayOnRight:Boolean=False, Time:Time=#00:00:00#, MessageStatus*:MessageStatus
- `Content/FlipContent`: StartsFlipped:Boolean=False, FlipOnClick:Boolean=True
- `Content/FloatingContent`: Position*:Position, UseFullHeight:Boolean=False, UseFullWidth:Boolean=False, UseMargin:Boolean=True
- `Content/ListItemContent`
- `Content/Section`: UsePadding:Boolean=True
- `Content/SectionGroup`: HasStickyTitles:Boolean=True, TopPosition:Integer=0
- `Content/Tag`: Color:Color=Primary, Size:Size=NullIdentifier(), Shape:Shape=Rounded, IsLight:Boolean=False
- `Content/Tooltip`: Position:Position=Right, StartsOpen:Boolean=False, Trigger:Trigger=OnHover
- `Content/UserAvatar`: Name:Text="Jonh Doe", Image:Binary Data=empty binary, Color:Color=Primary, Size:Size=NullIdentifier(), Shape:Shape=Rounded, IsLight:Boolean=False

## Interaction

- `Interaction/ActionSheet`: IsOpen*:Boolean
- `Interaction/Animate`: AnimationType*:AnimationType, Delay:Integer=0, Speed:Speed=NullIdentifier()
- `Interaction/AnimatedLabel`
- `Interaction/BottomSheet`: Shape:Shape=SoftRounded, ShowHandler:Boolean=True
- `Interaction/Carousel`: Navigation:CarouselNavigation=Both, Height:Text="auto", ItemsPerSlide:CarouselItems=empty CarouselItems, OptionalConfigs:CarouselOptionalConfigs=empty CarouselOptionalConfigs
- `Interaction/DatePicker`: DateFormat:Text, ShowTodayButton:Boolean=False, TimeFormat:DatePickerTimeFormat=Disabled, OptionalConfigs:DatePickerOptionalConfigs=empty DatePickerOptionalConfigs
- `Interaction/DatePickerRange`: DateFormat:Text, ShowTodayButton:Boolean=False, OptionalConfigs:DatePickerRangeOptionalConfigs=empty DatePickerRangeOptionalConfigs
- `Interaction/DropdownSearch`: OptionsList*:DropdownOption, StartingSelection:DropdownOption=empty list, Prompt:Text="Select...", OptionalConfigs:DropdownOptionalConfigs=empty DropdownOptionalConfigs
- `Interaction/DropdownTags`: OptionsList*:DropdownOption, StartingSelection:DropdownOption=empty list, Prompt:Text="Select...", OptionalConfigs:DropdownTagsOptionalConfigs=empty DropdownTagsOptionalConfigs
- `Interaction/FloatingActions`: IsExpanded:Boolean=False, IsHover:Boolean=False
- `Interaction/FloatingActionsItem`
- `Interaction/InputWithIcon`: AlignIconRight:Boolean=False
- `Interaction/LightboxImage`: Title:Text, Group:Text, ImageURL:Text, ImageZoom:Decimal=2, OptionalConfigs:LightboxImageOptionalConfigs=empty LightboxImageOptionalConfigs
- `Interaction/MonthPicker`: DateFormat:Text="MM/YYYY", InitialMonth:MonthYear=empty MonthYear, MinMonth:MonthYear=empty MonthYear, MaxMonth:MonthYear=empty MonthYear
- `Interaction/Notification`: StartsOpen:Boolean=False, Width:Text="370px", Position:Position=Top, OptionalConfigs:NotificationOptionalConfigs=empty NotificationOptionalConfigs
- `Interaction/RangeSlider`: MinValue*:Decimal, MaxValue*:Decimal, StartingValue*:Decimal, Orientation:Orientation=Horizontal, Size:Text="100%", OptionalConfigs:RangeSliderOptionalConfigs=empty RangeSliderOptionalConfigs
- `Interaction/RangeSliderInterval`: MinValue*:Decimal, MaxValue*:Decimal, StartingValueFrom*:Decimal, StartingValueTo*:Decimal, Orientation:Orientation=Horizontal, Size:Text="100%", OptionalConfigs:RangeSliderOptionalConfigs=empty RangeSliderOptionalConfigs
- `Interaction/ScrollableArea`: Orientation:Orientation=Horizontal, Height:Text, Width:Text, ScrollbarStyle:ScrollbarStyle=Default
- `Interaction/Search`
- `Interaction/Sidebar`: StartsOpen:Boolean=False, Direction:Direction=Right, HasOverlay:Boolean=False, Width:Text="500px"
- `Interaction/StackedCards`: StackedOptions:StackedCardsPosition=Bottom, Rotate:Boolean=True, Items:Integer=5, ElementsMargin:Integer=5, UseOverlays:Boolean=True
- `Interaction/TimePicker`: TimeFormat:Text, Is24Hours:Boolean=True, InitialTime:Time=#00:00:00#, OptionalConfigs:TimePickerOptionalConfigs=empty TimePickerOptionalConfigs
- `Interaction/Video`: URL*:Text, Controls:Boolean=True, Width:Text, Height:Text, Captions:VideoCaptions=empty list, OptionalConfigs:VideoOptionalConfigs=empty VideoOptionalConfigs

## Navigation

- `Navigation/BottomBarItem`
- `Navigation/Breadcrumbs`
- `Navigation/BreadcrumbsItem`
- `Navigation/OverflowMenu`: BalloonShape:Shape=SoftRounded, BalloonPosition:FloatingPosition=NullIdentifier()
- `Navigation/Pagination`: StartIndex*:Integer, MaxRecords*:Integer, TotalCount*:Long Integer, ShowGoToPage:Boolean=False
- `Navigation/SectionIndex`: SmoothScrolling:Boolean=True, IsFixed:Boolean=False
- `Navigation/SectionIndexItem`: ScrollToWidgetId*:Text
- `Navigation/Submenu`
- `Navigation/Tabs`: TabsOrientation:Orientation=Horizontal, StartingTab:Integer=0, Height:Text="auto", TabsVerticalPosition:Direction=Left, OptionalConfigs:TabsOptionalConfigs=empty TabsOptionalConfigs
- `Navigation/TabsContentItem`
- `Navigation/TabsHeaderItem`
- `Navigation/TimelineItem`: IsActive:Boolean=False, Color:Color=Primary
- `Navigation/Wizard`: IsVertical:Boolean=False, StepsBehaviour:StepsBehaviour=Interactive
- `Navigation/WizardItem`: Status*:Steps, ReverseLabelPosition:Boolean=False

## Numbers

- `Numbers/Badge`: Number*:Long Integer, Color:Color=Primary, Size:Size=NullIdentifier(), Shape:Shape=Rounded, IsLight:Boolean=False
- `Numbers/Counter`: BackgroundColor:Color=Neutral0, IsVertical:Boolean=False, Height:Text="100"
- `Numbers/IconBadge`: Number*:Long Integer, Color:Color=Primary, IsLight:Boolean=False
- `Numbers/ProgressBar`: Progress*:Integer, ProgressColor:Color=Primary, TrailColor:Color=Neutral4, Thickness:Integer=12, OptionalConfigs:ProgressBarOptionalConfigs=empty ProgressBarOptionalConfigs
- `Numbers/ProgressCircle`: Progress*:Integer, ProgressColor:Color=Primary, Size:Text="auto", TrailColor:Color=Neutral4, Thickness:Integer=8, OptionalConfigs:ProgressCircleOptionalConfigs=empty ProgressCircleOptionalConfigs
- `Numbers/Rating`: RatingValue*:Decimal, RatingScale:Integer=5, IsEdit:Boolean=False, Size:Size=NullIdentifier()

## Utilities

- `Utilities/AlignCenter`: IsHorizontal:Boolean=True
- `Utilities/ButtonLoading`: IsLoading*:Boolean, ShowLabelOnLoading:Boolean=False
- `Utilities/CenterContent`: Height:Integer=0
- `Utilities/InlineSVG`: SVGCode:Text
- `Utilities/MarginContainer`
- `Utilities/MouseEvents`: WidgetId*:Text, PreventDefaults:Boolean=True
- `Utilities/PasswordPolicy`: Password*:Text
- `Utilities/ProviderLoginButton`: IdentityProvider*:IdentityProvider, IconOnly:Boolean=False, Shape:Shape=SoftRounded
- `Utilities/Separator`: IsVertical:Boolean=False, Space:Space=Base, Color:Color=Neutral4
- `Utilities/SwipeEvents`: WidgetId*:Text
- `Utilities/TouchEvents`: WidgetId*:Text, PreventDefaults:Boolean=True

## Enum values

Identifier parameters take `Entities.<Enum>.<Value>`.

- AccordionIconPosition: Left, Right
- AccordionIconType: Caret, Custom, PlusMinus
- Alert: Error, Info, Success, Warning
- AnimationType: BottomToTop, Bounce, FadeIn, LeftToRight, RightToLeft, Scale, ScaleDown, Spinner, TopToBottom
- BreakColumns: All, First, Last, Middle, None
- CarouselNavigation: Arrows, Both, Dots, None
- Color: Blue, Cyan, Grape, Green, Indigo, Lime, Neutral0, Neutral1, Neutral10, Neutral2, Neutral3, Neutral4, Neutral5, Neutral6, Neutral7, Neutral8, Neutral9, Orange, Pink, Primary, Red, Secondary, Teal, Transparent, Violet, Yellow
- DatePickerTimeFormat: Disabled, Time12hFormat, Time24hFormat
- Direction: Left, Right
- FloatingPosition: Auto, Bottom, BottomEnd, BottomStart, Center, Left, LeftEnd, LeftStart, Right, RightEnd, RightStart, Top, TopEnd, TopStart
- GutterSize: Base, ExtraLarge, ExtraSmall, Large, Medium, None, Small, XXLarge
- IdentityProvider: Apple, Facebook, Google
- MessageStatus: Hidden, Read, Received, Sent
- Orientation: Horizontal, Vertical
- Position: Bottom, BottomLeft, BottomRight, Center, Left, Right, Top, TopLeft, TopRight
- ScrollbarStyle: Compact, Default, None
- Shape: Rounded, Sharp, SoftRounded
- Size: Medium, Small
- Space: Base, ExtraLarge, ExtraSmall, Large, Medium, None, Small, XXLarge
- Speed: Fast, Normal, Slow
- StackedCardsPosition: Bottom, None, Top
- Steps: Active, Next, Past
- StepsBehaviour: Interactive, ProgressOnly
- Trigger: OnClick, OnHover
