from fpdf import FPDF
from pathlib import Path


class ContractPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "CONFIDENTIAL", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def make_contract(title: str, body: str, filename: str):
    pdf = ContractPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "", 11)
    for line in body.strip().split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(4)
        elif line.isupper() and len(line) > 3:
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
        else:
            pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")

    path = Path(__file__).parent / filename
    pdf.output(str(path))
    print(f"  Generated: {filename} ({path.stat().st_size / 1024:.1f} KB)")


# ── Contract A: High risk ──────────────────────────────────────────────

contract_a = """SERVICE AGREEMENT

THIS SERVICE AGREEMENT (the "Agreement") is entered into on the date of last signature (the "Effective Date") by and between TechVendor Inc., a Delaware corporation ("Vendor"), and ClientCorp Ltd. ("Client").

1. SERVICES
Vendor shall provide the services described in Exhibit A (the "Services"). Vendor may subcontract any or all of its obligations without Client's prior written consent.

2. PAYMENT TERMS
Client shall pay Vendor the fees set forth in Exhibit B. All fees are non-refundable. Vendor may increase fees by up to 25% annually upon 15 days' written notice. Late payments shall incur interest at 5% per month, compounded daily. Client shall pay all fees within 15 days of invoice date, regardless of whether Services have been performed satisfactorily. If Client disputes any invoice, Client must still pay the full amount and seek reimbursement later. Vendor reserves the right to suspend all Services immediately if any invoice remains unpaid for more than 3 days after the due date, without liability.

3. TERM AND TERMINATION
This Agreement shall have an initial term of 36 months. Thereafter, this Agreement shall automatically renew for successive 12-month periods unless either party provides written notice of non-renewal at least 180 days prior to the end of the then-current term. Client may terminate this Agreement for convenience only upon 365 days' prior written notice and payment of a termination fee equal to 80% of the remaining fees due under the Agreement. Vendor may terminate this Agreement immediately upon written notice if Client breaches any term, fails to make payment when due, or for any reason or no reason at all.

4. LIABILITY AND INDEMNIFICATION
VENDOR'S TOTAL LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED THE TOTAL FEES PAID BY CLIENT IN THE PRECEDING 12 MONTHS. IN NO EVENT SHALL VENDOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS OR LOSS OF DATA. Vendor shall not be liable for any damages resulting from service interruptions, data breaches, or security incidents. Client agrees to indemnify, defend, and hold Vendor harmless from any and all claims arising out of Client's use of the Services, including claims caused solely by Vendor's negligence or breach of this Agreement.

5. INTELLECTUAL PROPERTY
All intellectual property rights in any deliverables, work product, software, or materials created by Vendor in connection with the Services shall be owned exclusively by Vendor. Vendor grants Client a non-exclusive, non-transferable, non-sublicensable, revocable license to use the deliverables solely during the term of this Agreement. Any improvements, suggestions, or feedback provided by Client shall be automatically assigned to Vendor free of charge.

6. CONFIDENTIALITY
Vendor may disclose Client's confidential information to its affiliates, subcontractors, and agents without restriction. Vendor's confidentiality obligations expire 12 months after the Effective Date. Vendor may use Client's confidential information for any purpose not expressly prohibited by law.

7. DATA PROTECTION AND SECURITY
Client acknowledges that Vendor does not guarantee the security of Client's data. Vendor may process Client's data in any country where Vendor operates. Client is solely responsible for maintaining backups of all data. Vendor may delete Client's data at any time upon 7 days' notice.

8. GOVERNING LAW AND DISPUTE RESOLUTION
This Agreement shall be governed by the laws of the Republic of Freedonia. Any disputes arising out of this Agreement shall be resolved exclusively through binding arbitration in the Republic of Freedonia, and Client waives any right to participate in a class action. Each party shall bear its own legal costs regardless of outcome."""

# ── Contract B: Moderate risk ───────────────────────────────────────────

contract_b = """MASTER SERVICES AGREEMENT

This Master Services Agreement ("MSA") is made effective as of the date of last signature by and between CloudStack Solutions Inc. ("Provider") and Acme Enterprises Inc. ("Customer").

1. SCOPE OF SERVICES
Provider will deliver the cloud infrastructure services described in the applicable Statement of Work ("SOW"). Each SOW, when executed by both parties, shall be governed by this MSA.

2. FEES AND PAYMENT
Customer shall pay the fees set forth in each SOW within 30 days of invoice date. Provider may adjust fees annually based on the Consumer Price Index, with 60 days' written notice. Late payments shall accrue interest at 1.5% per month. Provider may suspend services if fees remain unpaid for 30 days after the due date, but will provide Customer 10 business days' prior written notice before any suspension.

3. TERM AND TERMINATION
This MSA shall remain in effect for 24 months from the Effective Date and shall renew for successive 12-month terms unless either party gives 90 days' written notice of non-renewal. Either party may terminate this MSA (i) for material breach if the breach remains uncured for 30 days after written notice, or (ii) immediately upon the other party's insolvency. Customer may terminate any SOW for convenience upon 90 days' written notice, subject to payment of fees through the notice period.

4. LIMITATION OF LIABILITY
Neither party shall be liable for any indirect, incidental, or consequential damages. Each party's total liability arising out of this MSA shall not exceed the total fees paid or payable by Customer under the applicable SOW during the 12 months preceding the claim. These limitations do not apply to (i) either party's indemnification obligations, (ii) Customer's payment obligations, (iii) breach of confidentiality, or (iv) gross negligence or willful misconduct.

5. INTELLECTUAL PROPERTY
Each party retains ownership of its pre-existing intellectual property. Provider grants Customer a non-exclusive, perpetual, worldwide license to use any deliverables created specifically for Customer under each SOW. Customer grants Provider a non-exclusive license to use Customer's materials solely for providing the Services.

6. CONFIDENTIALITY
Each party agrees to protect the other's confidential information using reasonable care, for a period of 3 years from disclosure. Confidential information may be disclosed only to those employees and contractors who need to know and are bound by confidentiality obligations at least as protective as those herein. This section does not apply to information that: (a) is or becomes publicly available through no fault of the receiving party; (b) was rightfully in the receiving party's possession prior to disclosure; or (c) is independently developed by the receiving party.

7. DATA PROTECTION
Provider shall maintain commercially reasonable administrative, physical, and technical security measures. Provider will process Customer data in accordance with the Data Processing Agreement attached as Exhibit A. Provider will delete Customer data within 90 days of termination upon Customer's written request.

8. GOVERNING LAW
This MSA shall be governed by the laws of the State of New York. Any dispute shall be resolved in the state or federal courts located in New York County, New York. The prevailing party shall be entitled to recover its reasonable legal costs."""

# ── Contract C: Low risk (well-balanced) ────────────────────────────────

contract_c = """PROFESSIONAL SERVICES AGREEMENT

This Professional Services Agreement ("Agreement") is entered into on the date set forth on the signature page by and between ConsultPro LLC ("Consultant") and BetaWorks Inc. ("Client").

1. SERVICES AND DELIVERABLES
Consultant will provide the professional services described in each Scope of Work ("SOW") attached hereto. Consultant shall perform all services in a professional and workmanlike manner, in accordance with industry standards. Consultant shall not subcontract any portion of the Services without Client's prior written consent, which shall not be unreasonably withheld.

2. COMPENSATION AND PAYMENT
Client shall pay Consultant the fees set forth in each SOW. Fees are fixed for the duration of the applicable SOW and may not be increased without mutual written agreement. Consultant will invoice Client monthly in arrears. Payment is due within 45 days of invoice date. Late payments shall accrue interest at 0.5% per month. Consultant may suspend services only after providing 15 business days' written notice of non-payment and only if the disputed amount exceeds $5,000.

3. TERM AND TERMINATION
This Agreement shall continue for 12 months from the Effective Date and may be renewed by mutual written agreement. Either party may terminate this Agreement or any SOW for convenience upon 30 days' written notice. Either party may terminate immediately upon written notice if the other party commits a material breach and fails to cure within 30 days of receiving written notice specifying the breach.

4. LIMITATION OF LIABILITY
Neither party excludes liability for: (a) death or personal injury caused by its negligence; (b) fraud or fraudulent misrepresentation; (c) breach of confidentiality obligations; (d) infringement of intellectual property rights; or (e) any liability that cannot be excluded by applicable law. Subject to the foregoing, each party's total aggregate liability shall not exceed the total fees paid under the applicable SOW. Neither party shall be liable for indirect or consequential damages.

5. INTELLECTUAL PROPERTY
All work product created by Consultant under any SOW shall be owned by Client upon full payment of fees. Consultant retains the right to use general knowledge, skills, and experience gained during performance. Consultant agrees to execute all documents reasonably necessary to perfect Client's ownership rights.

6. CONFIDENTIALITY
Each party agrees to maintain the confidentiality of the other's confidential information for a period of 5 years. Confidential information may be shared only with personnel who have a need to know and are bound by equivalent confidentiality obligations. Each party shall return or destroy the other's confidential information within 60 days of a written request upon termination.

7. DATA SECURITY
Consultant agrees to implement and maintain appropriate technical and organizational security measures, including encryption of data in transit and at rest, access controls, regular security assessments, and breach notification within 48 hours. Consultant shall comply with all applicable data protection laws. A Data Processing Agreement is attached as Exhibit B.

8. GOVERNING LAW
This Agreement shall be governed by the laws of the State of Delaware. Any dispute arising out of this Agreement shall be resolved through good-faith negotiations, then mediation, and finally binding arbitration in Wilmington, Delaware. Each party shall bear its own legal fees, and the arbitrator may award fees to the prevailing party if the other party's position was frivolous."""


if __name__ == "__main__":
    print("Generating sample contracts...\n")

    make_contract("Service Agreement", contract_a, "contract_high_risk.pdf")
    make_contract("Master Services Agreement", contract_b, "contract_moderate_risk.pdf")
    make_contract("Professional Services Agreement", contract_c, "contract_low_risk.pdf")

    print("\nDone! 3 sample contracts generated.")
