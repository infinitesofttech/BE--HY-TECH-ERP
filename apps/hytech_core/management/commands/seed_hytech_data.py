import os
import json
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.hytech_customers.models import Customer, FamilyMember, CustomerDocument, ServiceVisit, VisitDocument
from apps.hytech_services.models import BaseService, SubService, RequiredDocument, Transaction
from apps.hytech_operations.models import Reminder, FollowUp, PendingWork, Application
from apps.hytech_hrms.models import AttendanceRecord, LeaveRecord, LeaveBalance, HolidayItem
from apps.hytech_demographics.models import Village, ContactInquiry, AuditLog
from apps.hytech_core.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds complete HY-TECH ERP dataset matching frontend mockData and catalog'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding HY-TECH ERP data..."))

        # 1. Staff & Admin Accounts
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hytech.com',
                'first_name': 'Mitali',
                'last_name': 'Changani',
                'role': 'super_admin',
                'phone': '9876543210',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.save()

        staff_user, _ = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@hytech.com',
                'first_name': 'Rahul',
                'last_name': 'Mehta',
                'role': 'operation_executive',
                'phone': '9825123456',
                'is_staff': True,
            }
        )
        staff_user.set_password('Staff@123')
        staff_user.save()

        self.stdout.write(self.style.SUCCESS("[OK] Admin & Staff accounts created"))

        # 2. Base Services (45 Services from catalogData.json)
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'catalogData.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                catalog_services = json.load(f)

            for item in catalog_services:
                base_svc, _ = BaseService.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'ServiceName': item.get('ServiceName', ''),
                        'ServiceNameGu': item.get('ServiceNameGu', ''),
                        'Category': item.get('Category', 'GOVT_FORMS'),
                        'SubCategory': item.get('SubCategory', ''),
                        'Department': item.get('Department', ''),
                        'ServiceType': item.get('ServiceType', 'NEW'),
                        'Description': item.get('Description', ''),
                        'GovernmentFee': Decimal(str(item.get('GovernmentFee', 0))),
                        'ServiceCharge': Decimal(str(item.get('ServiceCharge', 0))),
                        'TotalFee': Decimal(str(item.get('TotalFee', 0))),
                        'SlaDays': item.get('SlaDays', 7),
                        'Priority': item.get('Priority', 'MEDIUM'),
                        'SmsTemplateGu': item.get('SmsTemplateGu', ''),
                        'SmsTemplateEn': item.get('SmsTemplateEn', ''),
                        'StaffInstructions': item.get('StaffInstructions', ''),
                        'FormFields': item.get('FormFields', []),
                        'PortalUrl': item.get('PortalUrl'),
                        'IsOfficial': item.get('IsOfficial', True),
                        'IsActive': item.get('IsActive', True),
                    }
                )

                sub_services = item.get('SubServices') or item.get('sub_services') or []
                for sub in sub_services:
                    sub_svc, _ = SubService.objects.update_or_create(
                        id=sub['id'],
                        defaults={
                            'Service': base_svc,
                            'SubServiceName': sub.get('SubServiceName', ''),
                            'Description': sub.get('Description', ''),
                            'IsActive': sub.get('IsActive', True),
                        }
                    )

                    req_docs = sub.get('RequiredDocuments') or sub.get('required_documents') or []
                    for req in req_docs:
                        RequiredDocument.objects.update_or_create(
                            id=req['id'],
                            defaults={
                                'SubService': sub_svc,
                                'DocumentName': req.get('DocumentName', ''),
                                'document_type': req.get('document_type', 'AADHAR'),
                                'IsRequired': req.get('IsRequired', True),
                            }
                        )

            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(catalog_services)} Base Services with Sub-Services & Required Documents"))

        # 3. Villages
        villages_data = [
            {'code': 'VIL-001', 'name': 'Varna', 'name_gu': 'વરણા', 'taluka': 'Dhanera', 'district': 'Banaskantha', 'total_families': 45, 'total_citizens': 182, 'total_documents': 520, 'male_count': 94, 'female_count': 88},
            {'code': 'VIL-002', 'name': 'Bota', 'name_gu': 'બોટા', 'taluka': 'Dhanera', 'district': 'Banaskantha', 'total_families': 62, 'total_citizens': 240, 'total_documents': 680, 'male_count': 122, 'female_count': 118},
            {'code': 'VIL-003', 'name': 'Gunjar', 'name_gu': 'ગુંજાર', 'taluka': 'Dhanera', 'district': 'Banaskantha', 'total_families': 38, 'total_citizens': 156, 'total_documents': 440, 'male_count': 80, 'female_count': 76},
            {'code': 'VIL-004', 'name': 'Malotra', 'name_gu': 'માલોત્રા', 'taluka': 'Dhanera', 'district': 'Banaskantha', 'total_families': 54, 'total_citizens': 210, 'total_documents': 590, 'male_count': 108, 'female_count': 102},
            {'code': 'VIL-005', 'name': 'Nenava', 'name_gu': 'નેનાવા', 'taluka': 'Dhanera', 'district': 'Banaskantha', 'total_families': 70, 'total_citizens': 285, 'total_documents': 790, 'male_count': 145, 'female_count': 140},
        ]
        for v in villages_data:
            Village.objects.update_or_create(code=v['code'], defaults=v)
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Villages"))

        # 4. Customers & Family Members
        c1, _ = Customer.objects.update_or_create(
            family_id='HTF-000001',
            defaults={
                'registration_date': '2026-08-25',
                'head_of_family': 'Vitthalbhai Changani',
                'mobile_number': '6789012345',
                'whatsapp_number': '8000231124',
                'family_member_count': 5,
                'village_city': 'Bota',
                'birth_date': '1985-05-23',
                'referral_family_id': 'HTF-000002',
                'document_consent': True,
                'current_points': 25,
                'wallet_balance': Decimal('0.00'),
                'total_visits': 2,
                'notes': 'Primary household with verified biometric Aadhaar cards',
                'digital_card_sent': True
            }
        )

        m1_1, _ = FamilyMember.objects.update_or_create(
            customer=c1, name='Vitthalbhai Changani',
            defaults={'relationship': 'HEAD', 'gender': 'MALE', 'mobile_number': '6789012345', 'birth_date': '1985-05-23'}
        )
        m1_2, _ = FamilyMember.objects.update_or_create(
            customer=c1, name='Jasumatiben Changani',
            defaults={'relationship': 'WIFE', 'gender': 'FEMALE', 'mobile_number': '8000231124', 'birth_date': '1988-08-14'}
        )
        m1_3, _ = FamilyMember.objects.update_or_create(
            customer=c1, name='Bhavik Changani',
            defaults={'relationship': 'SON', 'gender': 'MALE', 'mobile_number': '6789012345', 'birth_date': '2010-03-12'}
        )
        m1_4, _ = FamilyMember.objects.update_or_create(
            customer=c1, name='Pooja Changani',
            defaults={'relationship': 'DAUGHTER', 'gender': 'FEMALE', 'mobile_number': '8000231124', 'birth_date': '2013-11-20'}
        )
        m1_5, _ = FamilyMember.objects.update_or_create(
            customer=c1, name='Govindbhai Changani',
            defaults={'relationship': 'FATHER', 'gender': 'MALE', 'mobile_number': '6789012345', 'birth_date': '1958-02-10'}
        )

        c2, _ = Customer.objects.update_or_create(
            family_id='HTF-000002',
            defaults={
                'registration_date': '2026-08-26',
                'head_of_family': 'Dineshbhai Changani',
                'mobile_number': '8000231125',
                'whatsapp_number': '6354456881',
                'family_member_count': 6,
                'village_city': 'Bota',
                'birth_date': '1974-04-12',
                'referral_family_id': 'HTF-000001',
                'document_consent': True,
                'current_points': 40,
                'wallet_balance': Decimal('50.00'),
                'total_visits': 3,
                'notes': 'Bota agricultural family with complete digital vault',
                'digital_card_sent': True
            }
        )

        m2_1, _ = FamilyMember.objects.update_or_create(
            customer=c2, name='Dineshbhai Changani',
            defaults={'relationship': 'HEAD', 'gender': 'MALE', 'mobile_number': '8000231125', 'birth_date': '1974-04-12'}
        )
        m2_2, _ = FamilyMember.objects.update_or_create(
            customer=c2, name='Geetaben Changani',
            defaults={'relationship': 'WIFE', 'gender': 'FEMALE', 'mobile_number': '6354456881', 'birth_date': '1978-06-19'}
        )
        m2_3, _ = FamilyMember.objects.update_or_create(
            customer=c2, name='Milan Changani',
            defaults={'relationship': 'SON', 'gender': 'MALE', 'mobile_number': '8000231125', 'birth_date': '2001-09-05'}
        )
        m2_4, _ = FamilyMember.objects.update_or_create(
            customer=c2, name='Priyaben Changani',
            defaults={'relationship': 'DAUGHTER', 'gender': 'FEMALE', 'mobile_number': '6354456881', 'birth_date': '2004-12-22'}
        )

        # 5. Customer Digital Vault Documents
        CustomerDocument.objects.update_or_create(
            customer=c1, family_member=m1_1, document_type='AADHAR',
            defaults={'document_name': 'Aadhaar Card - Vitthalbhai', 'is_verified': True}
        )
        CustomerDocument.objects.update_or_create(
            customer=c1, family_member=m1_1, document_type='PAN',
            defaults={'document_name': 'PAN Card - Vitthalbhai', 'is_verified': True}
        )
        CustomerDocument.objects.update_or_create(
            customer=c1, document_type='RATION_CARD',
            defaults={'document_name': 'Barcoded Ration Card - Bota', 'is_verified': True}
        )
        CustomerDocument.objects.update_or_create(
            customer=c2, family_member=m2_1, document_type='AADHAR',
            defaults={'document_name': 'Aadhaar Card - Dineshbhai', 'is_verified': True}
        )
        CustomerDocument.objects.update_or_create(
            customer=c2, family_member=m2_2, document_type='AADHAR',
            defaults={'document_name': 'Aadhaar Card - Geetaben', 'is_verified': True}
        )
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Customers, Members & Digital Vault"))

        # 6. Service Visits
        first_svc = BaseService.objects.first()
        first_sub = SubService.objects.filter(Service=first_svc).first() if first_svc else None

        visit1, _ = ServiceVisit.objects.update_or_create(
            visit_no='VIS-000001',
            defaults={
                'customer': c1,
                'family_member': m1_1,
                'service': first_svc,
                'sub_service': first_sub,
                'checked_by': staff_user,
                'status': 'COMPLETED',
                'visit_date': timezone.now().date() - timedelta(days=2),
                'remarks': 'Document scrutiny complete. Customer received acknowledgement.'
            }
        )
        VisitDocument.objects.update_or_create(
            visit=visit1, document_name='Aadhaar Card',
            defaults={'document_type': 'AADHAR', 'status': 'AVAILABLE'}
        )
        VisitDocument.objects.update_or_create(
            visit=visit1, document_name='Ration Card',
            defaults={'document_type': 'RATION_CARD', 'status': 'AVAILABLE'}
        )

        visit2, _ = ServiceVisit.objects.update_or_create(
            visit_no='VIS-000002',
            defaults={
                'customer': c2,
                'family_member': m2_1,
                'service': first_svc,
                'sub_service': first_sub,
                'checked_by': staff_user,
                'status': 'IN_PROGRESS',
                'visit_date': timezone.now().date(),
                'remarks': 'Biometric update initiated. Waiting for OTP confirmation.'
            }
        )
        VisitDocument.objects.update_or_create(
            visit=visit2, document_name='Aadhaar Card',
            defaults={'document_type': 'AADHAR', 'status': 'AVAILABLE'}
        )
        VisitDocument.objects.update_or_create(
            visit=visit2, document_name='Electricity Bill / Address Proof',
            defaults={'document_type': 'OTHER', 'status': 'NOT_AVAILABLE'}
        )

        self.stdout.write(self.style.SUCCESS("[OK] Seeded Service Visits & Checklists"))

        # 7. Transactions
        Transaction.objects.update_or_create(
            transaction_no='TXN-000001',
            defaults={
                'transaction_date': timezone.now().date() - timedelta(days=2),
                'customer': c1,
                'service': first_svc,
                'sub_service': first_sub,
                'staff': staff_user,
                'bill_amount': Decimal('150.00'),
                'paid_amount': Decimal('150.00'),
                'due_amount': Decimal('0.00'),
                'payment_status': 'PAID',
                'payment_mode': 'UPI',
                'points_earned': 1,
                'points_redeemed': 0,
                'remarks': 'Online UPI Payment via PhonePe',
                'items': [{'service_name': first_svc.ServiceName if first_svc else 'PMAY', 'amount': 150}]
            }
        )
        Transaction.objects.update_or_create(
            transaction_no='TXN-000002',
            defaults={
                'transaction_date': timezone.now().date(),
                'customer': c2,
                'service': first_svc,
                'sub_service': first_sub,
                'staff': staff_user,
                'bill_amount': Decimal('300.00'),
                'paid_amount': Decimal('250.00'),
                'due_amount': Decimal('50.00'),
                'payment_status': 'PARTIAL',
                'payment_mode': 'CASH',
                'points_earned': 3,
                'points_redeemed': 0,
                'remarks': '₹50 balance pending on final delivery',
                'items': [{'service_name': first_svc.ServiceName if first_svc else 'Aadhaar', 'amount': 300}]
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Billing Transactions"))

        # 8. Reminders & Follow-ups
        r1, _ = Reminder.objects.update_or_create(
            reminder_no='RMD-000001',
            defaults={
                'customer': c1,
                'service': first_svc,
                'reminder_type': 'SERVICE_READY',
                'subject': 'Aadhaar Card Ready for Collection',
                'due_date': timezone.now().date() + timedelta(days=2),
                'reminder_date': timezone.now().date(),
                'priority': 'HIGH',
                'message_template': 'નમસ્તે Vitthalbhai, તમારું આધાર કાર્ડ તૈયાર છે. HY-TECH સેન્ટર પરથી લઈ જવું.',
                'follow_up_status': 'PENDING',
                'notes': 'Customer requested laminated printout',
                'created_by': staff_user
            }
        )
        FollowUp.objects.update_or_create(
            reminder=r1,
            defaults={
                'contact_date': timezone.now().strftime('%Y-%m-%d %H:%M'),
                'customer_response': 'Citizen confirmed visit tomorrow morning.',
                'next_follow_up': timezone.now().date() + timedelta(days=1),
                'notes': 'Spoke with son Bhavik',
                'contacted_by': staff_user
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Reminders & Follow-ups"))

        # 9. Pending Work Kanban
        PendingWork.objects.update_or_create(
            pending_no='PW-000001',
            defaults={
                'service_visit': visit2,
                'customer': c2,
                'service': first_svc,
                'pending_since': timezone.now().date() - timedelta(days=3),
                'expected_date': timezone.now().date() + timedelta(days=4),
                'priority': 'HIGH',
                'pending_reason': 'Govt UIDAI Portal OTP server slow. Resubmission scheduled.',
                'documents_pending': 'Electricity bill / Residence Certificate',
                'assigned_staff': staff_user,
                'next_action': 'Resubmit during non-peak hours',
                'work_status': 'IN_PROGRESS',
                'follow_up_date': timezone.now().date() + timedelta(days=1),
                'created_by': staff_user
            }
        )
        PendingWork.objects.update_or_create(
            pending_no='PW-000002',
            defaults={
                'customer': c1,
                'service': first_svc,
                'pending_since': timezone.now().date() - timedelta(days=5),
                'expected_date': timezone.now().date() + timedelta(days=2),
                'priority': 'MEDIUM',
                'pending_reason': 'Revenue Mamlatdar signature pending',
                'documents_pending': '',
                'assigned_staff': admin_user,
                'next_action': 'Follow up with Taluka office',
                'work_status': 'PENDING',
                'follow_up_date': timezone.now().date() + timedelta(days=2),
                'created_by': admin_user
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Pending Work Tickets"))

        # 10. Govt OS Applications
        Application.objects.update_or_create(
            application_no='APP-000001',
            defaults={
                'customer': c1,
                'family_member': m1_1,
                'applicant_name': 'Vitthalbhai Changani',
                'applicant_mobile': '6789012345',
                'service': first_svc,
                'sub_service': first_sub,
                'category': 'GOVT_FORMS',
                'status': 'SUBMITTED',
                'priority': 'HIGH',
                'government_app_no': 'GUJ-PMAY-2026-88912',
                'government_portal_url': 'https://pmayg.nic.in',
                'govt_fee': Decimal('0.00'),
                'service_charge': Decimal('150.00'),
                'total_fee': Decimal('150.00'),
                'payment_status': 'PAID',
                'payment_mode': 'UPI',
                'receipt_no': 'TXN-000001',
                'assigned_staff': staff_user,
                'created_by': staff_user,
                'expected_date': timezone.now().date() + timedelta(days=15),
                'sla_days': 15,
                'documents': [
                    {'id': 1, 'document_name': 'Aadhaar Card', 'document_type': 'AADHAR', 'status': 'VERIFIED'},
                    {'id': 2, 'document_name': 'Ration Card', 'document_type': 'RATION_CARD', 'status': 'VERIFIED'}
                ],
                'form_data': {'annual_income': 120000, 'housing_type': 'Kaccha House'},
                'timeline': [
                    {'id': 1, 'timestamp': timezone.now().isoformat(), 'actor_name': 'Rahul Mehta', 'actor_role': 'STAFF', 'action': 'Application created and documents verified'},
                    {'id': 2, 'timestamp': timezone.now().isoformat(), 'actor_name': 'Rahul Mehta', 'actor_role': 'STAFF', 'action': 'Submitted on PMAY Government Portal', 'new_status': 'SUBMITTED'}
                ]
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Applications"))

        # 11. Gujarat Government Holidays
        holidays_data = [
            {'title': 'Republic Day', 'title_gu': 'પ્રજાસત્તાક દિન', 'date': '2026-01-26', 'day': 'Monday', 'type': 'NATIONAL'},
            {'title': 'Dhuleti / Holi', 'title_gu': 'ધૂળેટી', 'date': '2026-03-04', 'day': 'Wednesday', 'type': 'REGIONAL'},
            {'title': 'Dr. Ambedkar Jayanti', 'title_gu': 'ડો. આંબેડકર જયંતિ', 'date': '2026-04-14', 'day': 'Tuesday', 'type': 'GOVERNMENT'},
            {'title': 'Gujarat Day', 'title_gu': 'ગુજરાત સ્થાપના દિન', 'date': '2026-05-01', 'day': 'Friday', 'type': 'REGIONAL'},
            {'title': 'Independence Day', 'title_gu': 'સ્વાતંત્ર્ય દિન', 'date': '2026-08-15', 'day': 'Saturday', 'type': 'NATIONAL'},
            {'title': 'Raksha Bandhan', 'title_gu': 'રક્ષાબંધન', 'date': '2026-08-28', 'day': 'Friday', 'type': 'REGIONAL'},
            {'title': 'Janmashtami', 'title_gu': 'જન્માષ્ટમી', 'date': '2026-09-04', 'day': 'Friday', 'type': 'GOVERNMENT'},
            {'title': 'Mahatma Gandhi Jayanti', 'title_gu': 'ગાંધી જયંતિ', 'date': '2026-10-02', 'day': 'Friday', 'type': 'NATIONAL'},
            {'title': 'Diwali', 'title_gu': 'દિવાળી', 'date': '2026-11-08', 'day': 'Sunday', 'type': 'GOVERNMENT'},
            {'title': 'Bestu Varas / New Year', 'title_gu': 'બેસતું વર્ષ', 'date': '2026-11-09', 'day': 'Monday', 'type': 'REGIONAL'},
        ]
        for h in holidays_data:
            HolidayItem.objects.update_or_create(date=h['date'], defaults=h)
        self.stdout.write(self.style.SUCCESS("[OK] Seeded Holidays"))

        # 12. HRMS Attendance & Leaves for Staff
        AttendanceRecord.objects.update_or_create(
            employee=staff_user,
            date=timezone.now().date(),
            defaults={
                'day_name': timezone.now().strftime('%A'),
                'in_time': '09:15 AM',
                'out_time': '06:30 PM',
                'status': 'PRESENT',
                'work_hours': 9.25,
                'notes': 'On-time front desk duty'
            }
        )
        LeaveBalance.objects.update_or_create(
            employee=staff_user,
            defaults={
                'casual_total': 12, 'casual_used': 2,
                'sick_total': 7, 'sick_used': 1,
                'paid_total': 5, 'paid_used': 1
            }
        )
        LeaveRecord.objects.update_or_create(
            employee=staff_user,
            start_date=timezone.now().date() + timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=11),
            defaults={
                'leave_type': 'CASUAL',
                'days_count': 2,
                'reason': 'Family religious ceremony in Banaskantha',
                'status': 'APPROVED',
                'approved_by': 'Mitali Changani'
            }
        )

        # 13. Audit Log & Public Inquiries
        AuditLog.objects.create(
            user_name='Mitali Changani',
            user_role='ADMIN',
            action='SEED_DATA',
            entity_type='SYSTEM',
            entity_id='INITIAL_SETUP',
            details='Initial system seed completed with 45 services, demo households, and staff accounts.',
            ip_address='127.0.0.1'
        )
        ContactInquiry.objects.update_or_create(
            mobile_number='9825123450',
            defaults={
                'full_name': 'Bipinbhai Patel',
                'email': 'bipin.patel@gmail.com',
                'subject': 'Aadhaar Card Address Update',
                'service_interest': 'Aadhaar Card Correction',
                'message': 'Need appointment for 3 members this Saturday morning',
                'status': 'NEW'
            }
        )

        Notification.objects.create(
            user=admin_user,
            title='HY-TECH ERP Live',
            message='System initialized and ready for citizen facilitation.',
            type='SUCCESS'
        )

        self.stdout.write(self.style.SUCCESS("=================================================="))
        self.stdout.write(self.style.SUCCESS("HY-TECH ERP SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("Staff Login: username=staff, password=Staff@123"))
        self.stdout.write(self.style.SUCCESS("Admin Login: username=admin, password=Admin@123"))
        self.stdout.write(self.style.SUCCESS("Customer Login: mobile=6789012345 or family_id=HTF-000001"))
        self.stdout.write(self.style.SUCCESS("=================================================="))
