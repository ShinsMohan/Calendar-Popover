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