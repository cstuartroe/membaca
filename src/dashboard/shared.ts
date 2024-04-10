const millisecondsInDay = 1000*60*60*24;

export const easinessColor = (easiness: number) => `hsl(${easiness*35}, 80%, 80%)`;

export function getUTCToday() {
    const today = new Date();
    today.setUTCHours(0);
    today.setUTCMinutes(0);
    today.setUTCSeconds(0);
    today.setMilliseconds(0);
    return today;
}

export function addDays(d: Date, days: number) {
    return new Date(d.getTime() + days*millisecondsInDay);
}

export function ISODate(d: Date) {
    return `${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}`;
}
