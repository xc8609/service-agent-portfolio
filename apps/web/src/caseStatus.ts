// Presentation only: delivery does not imply resolution or authorize closure.
export function caseStatus(status:string,feedbackStatus:string){
  return status==='awaiting_feedback'&&feedbackStatus==='completed'
    ?'Feedback delivered · case remains open'
    :status.replaceAll('_',' ');
}
