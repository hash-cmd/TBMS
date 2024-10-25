import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from branch.models import CustomerInformation
from .models import TreasuryBills, MaturedTBills
from accounts.models import CustomUser
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task
def check_database():
    now = timezone.now()
    matured_bills = TreasuryBills.objects.select_related('account_number').filter(maturity_date__lte=now)

    for bill in matured_bills:
        with transaction.atomic():
            matured_t_bill = MaturedTBills.objects.create(
                transaction_code=bill.transaction_code,
                branch_purchased_at=bill.branch_purchased_at,
                account_number=bill.account_number.account_number,
                csd_number=bill.account_number.csd_number,
                customer_name=f"{bill.account_number.surname_or_company_name} {bill.account_number.other_names}",
                customer_amount=bill.customer_amount,
                lcy_amount=bill.lcy_amount,
                face_value=bill.face_value,
                issue_date=bill.issue_date,
                maturity_date=bill.maturity_date,
                requested_by=bill.created_by
            )
            logger.info(f'Matured_T_Bill record created for Treasury Bill ID {bill.id}')

            if bill.maturity_instruction == 1:
                maturity_notification(bill)
                bill.delete()  
                logger.info(f'Treasury Bill ID {bill.id} deleted successfully.')
                continue  

            elif bill.maturity_instruction == 2:
                maturity_notification(bill)
                
                new_transaction_code = '033'

                new_treasury_bill = TreasuryBills(
                    transaction_code=new_transaction_code,
                    branch_purchased_at=bill.branch_purchased_at,
                    tenor=bill.tenor,
                    currency=bill.currency,
                    customer_amount=bill.face_value, 
                    created_by=bill.created_by,
                    roll_over_instruction='2', 
                    status=0
                )

                if bill.maturity_date.weekday() != 0:
                    next_monday = bill.maturity_date + timezone.timedelta(days=(7 - bill.maturity_date.weekday()))
                    new_value_date = next_monday
                else:
                    new_value_date = bill.maturity_date

                new_treasury_bill.issue_date = new_value_date
                new_treasury_bill.maturity_date = new_value_date + timezone.timedelta(days=bill.tenor)

                account_number = bill.account_number.account_number
                if account_number:
                    try:
                        customer_info = CustomerInformation.objects.get(account_number=account_number)
                        new_treasury_bill.account_number = customer_info
                    except CustomerInformation.DoesNotExist:
                        logger.warning(f"CustomerInformation not found for account number: {account_number}")

                new_treasury_bill.save()
                bill.delete()
                logger.info(f'New Treasury Bill created with ID {new_treasury_bill.id} and Transaction Code {new_treasury_bill.transaction_code}')

            elif bill.maturity_instruction == 3:
                maturity_notification(bill)
          
                new_transaction_code = '033'

                new_treasury_bill = TreasuryBills(
                    transaction_code=new_transaction_code,
                    branch_purchased_at=bill.branch_purchased_at,
                    tenor=bill.tenor,
                    currency=bill.currency,
                    customer_amount=bill.customer_amount, 
                    created_by=bill.created_by,
                    roll_over_instruction='3',
                    status='0' 
                )

                if bill.maturity_date.weekday() != 0:
                    next_monday = bill.maturity_date + timezone.timedelta(days=(7 - bill.maturity_date.weekday()))
                    new_value_date = next_monday
                else:
                    new_value_date = bill.maturity_date

                new_treasury_bill.issue_date = new_value_date
                new_treasury_bill.maturity_date = new_value_date + timezone.timedelta(days=bill.tenor)

                new_treasury_bill.save()
                logger.info(f'New Treasury Bill created with ID {new_treasury_bill.id} and Transaction Code {new_treasury_bill.transaction_code}')

  
            bill.save()
            bill.delete()
            logger.info(f'Treasury Bill ID {bill.id} updated successfully.')



def maturity_notification(bill):
    users_in_branch = CustomUser.objects.filter(branch_code=bill.Branch)
    for user in users_in_branch:
        try:
            send_mail(
                'Treasury Bill Maturity Alert',
                f'The Treasury Bill with ID {bill.Transaction_ID} has matured.\n\n'
                f'Details:\n'
                f'Account Number: {bill.Account_Number.Account_Number}\n'
                f'Principal Amount: {bill.Principal_Amount}\n'
                f'Face Value: {bill.Face_Value}\n'
                f'Value Date: {bill.Value_Date}\n'
                f'Maturity Date: {bill.Maturity_Date}\n',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f'Email sent to {user.email} for matured Treasury Bill ID {bill.id}')
        except Exception as e:
            logger.error(f'Failed to send email to {user.email} for matured Treasury Bill ID {bill.id}: {str(e)}')
