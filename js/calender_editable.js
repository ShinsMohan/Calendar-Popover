/** @odoo-module **/

export class CalendarCommonPopover extends Component {
    setup() {
    }

    async onSave() {
        const updatedData = {
            title: this.record.title,
            description: this.record.description,
        };
        await this.rpc({
            model: 'calendar.event',
            method: 'write',
            args: [[this.record.id], updatedData],
        });
        this.closePopover();
    }

    closePopover() {
    }
}

// /** @odoo-module **/
// import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";

// export class CustomCalendarCommonPopover extends CalendarCommonPopover {

//     getFieldEditMode(fieldInfo, record) {
//         return {
//             name: fieldInfo.name,
//             record: record,
//             fieldInfo: fieldInfo,
//             mode: "edit",
//         };
//     }

//     async onSaveEvent() {
//         try {
//             await this.props.record.save();
//             this.props.close();
//         } catch (error) {
//             console.error("Failed to save the event:", error);
//         }
//     }
// }

// CustomCalendarCommonPopover.template = "web.CalendarCommonPopover";
// CustomCalendarCommonPopover.subTemplates = {
//     ...CalendarCommonPopover.subTemplates,
//     body: "custom.CalendarCommonPopover.body",
//     footer: "custom.CalendarCommonPopover.footer",
// };