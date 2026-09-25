# -*- coding: utf-8 -*-
"""Page content. Each entry: path, title (<=60 chars ideal), description
(<=160 chars ideal), body HTML. Use [[ICON:name]] for icons and root-absolute
links (/about.html) so links also work from the 404 page at any URL depth.
Site copy uses "we", never "I".
"""
import json
from design import SITE_URL, SITE_NAME, EMAIL, PHONE_TEL, LINKEDIN

WEB3FORMS_KEY = "34ee8b9a-8fc9-46f6-b3f2-9fcbcecbf226"  # public by design (Web3Forms can only email the account owner)

CTA_BAND = """
<section class="cta-band" aria-labelledby="cta-title">
  <div class="container cta-inner">
    <div>
      <h2 id="cta-title">{title}</h2>
      <p>{text}</p>
    </div>
    <div class="hero-actions">
      <a href="/submit-a-business.html" class="btn btn-light btn-lg">Submit a Business</a>
      <a href="{href2}" class="btn btn-ghost-light btn-lg">{label2}</a>
    </div>
  </div>
</section>
"""


def cta(title, text, href2="/contact.html", label2="Contact Us"):
    return CTA_BAND.format(title=title, text=text, href2=href2, label2=label2)


def card(icon, title, text, index=None):
    idx = '<span class="card-index">%s</span>' % index if index else ""
    return ('<article class="card"><div class="card-icon">[[ICON:%s]]</div>%s<h3>%s</h3><p>%s</p></article>'
            % (icon, idx, title, text))


def criteria(rows):
    return '<dl class="criteria">' + "".join(
        "<div><dt>%s</dt><dd>%s</dd></div>" % r for r in rows) + "</dl>"


def timeline(steps):
    out = ['<ol class="timeline">']
    for i, (name, desc) in enumerate(steps, 1):
        final = " final" if i == len(steps) else ""
        out.append('<li class="step%s"><div class="box" aria-hidden="true">%d</div><div class="step-text">'
                   '<h4><span class="visually-hidden">Step %d: </span>%s</h4><div class="rule" aria-hidden="true"></div><p>%s</p></div></li>'
                   % (final, i, i, name, desc))
        if i < len(steps):
            out.append('<li class="arrow" aria-hidden="true">[[ICON:arrow]]</li>')
    out.append("</ol>")
    return "\n".join(out)


def field_error(fid):
    return '<p class="field-error" id="%s-error" hidden>[[ICON:alert]]<span></span></p>' % fid


def field(fid, label, name, *, kind="input", type_="text", required=False, maxlength=None,
          autocomplete=None, placeholder=None, hint=None, full=False, options=None, pattern=None,
          data_label=None, opt_note=None, minlength=None):
    req = '<span class="req" aria-hidden="true">*</span>' if required else ""
    optional = ' <span class="opt">%s</span>' % (opt_note or "(optional)") if not required else ""
    described = []
    if hint:
        described.append(fid + "-hint")
    described.append(fid + "-error")
    attrs = ['id="%s"' % fid, 'name="%s"' % name, 'aria-describedby="%s"' % " ".join(described),
             'data-label="%s"' % (data_label or label.lower())]
    if required:
        attrs.append("required")
    if maxlength:
        attrs.append('maxlength="%d"' % maxlength)
    if minlength:
        attrs.append('minlength="%d"' % minlength)
    if autocomplete:
        attrs.append('autocomplete="%s"' % autocomplete)
    if placeholder:
        attrs.append('placeholder="%s"' % placeholder)
    if pattern:
        attrs.append('pattern="%s"' % pattern)
    a = " ".join(attrs)
    if kind == "textarea":
        control = "<textarea %s></textarea>" % a
    elif kind == "select":
        opts = '<option value="">Select one</option>' + "".join("<option>%s</option>" % o for o in options)
        control = "<select %s>%s</select>" % (a, opts)
    else:
        control = '<input type="%s" %s>' % (type_, a)
    hint_html = '<p class="hint" id="%s-hint">%s</p>' % (fid, hint) if hint else ""
    return ('<div class="field%s"><label for="%s">%s%s%s</label>%s%s%s</div>'
            % (" full" if full else "", fid, label, req, optional, control, hint_html, field_error(fid)))


def form_open(subject):
    return """<form data-form action="https://api.web3forms.com/submit" method="POST" novalidate>
  <div id="form-alert" class="alert" role="alert" tabindex="-1" hidden>[[ICON:alert]]<div class="alert-body"></div></div>
  <input type="hidden" name="access_key" value="{key}">
  <input type="hidden" name="subject" value="{subject}">
  <input type="hidden" name="from_name" value="CJ Business Acquisitions Website">
  <div class="hp" aria-hidden="true"><label for="botcheck">Leave this empty</label><input type="checkbox" id="botcheck" name="botcheck" tabindex="-1" autocomplete="off"></div>
  <p class="hint">Fields marked <span class="req" aria-hidden="true">*</span><span class="visually-hidden">with an asterisk</span> are required.</p>
""".format(key=WEB3FORMS_KEY, subject=subject)


def form_close(button, legal):
    return """  <div class="form-foot">
    <div class="captcha-wrap">
      <div class="fieldset-label">Verification <span class="req" aria-hidden="true">*</span></div>
      <div id="captcha" class="captcha"></div>
      <p id="captcha-note" class="captcha-note">A quick spam check appears here once you start filling in the form.</p>
    </div>
    <button type="submit" class="btn btn-lg btn-block">{button}</button>
    <p class="form-legal">{legal}</p>
  </div>
</form>""".format(button=button, legal=legal)


PHONE_PATTERN = r"[0-9 +\(\)\.\-xXetEXT]{7,25}"
PAGES = []

# ===========================================================================
# HOME
# ===========================================================================
ORG_LD = json.dumps({
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Organization", "@id": SITE_URL + "/#org", "name": SITE_NAME, "url": SITE_URL + "/",
         "email": EMAIL, "telephone": PHONE_TEL, "logo": SITE_URL + "/apple-touch-icon.png",
         "areaServed": {"@type": "State", "name": "North Carolina"},
         "description": "Acquires and operates established engineering and manufacturing businesses in North Carolina.",
         "founder": {"@type": "Person", "name": "Chad Johnson", "jobTitle": "Principal", "sameAs": [LINKEDIN]}},
        {"@type": "WebSite", "@id": SITE_URL + "/#website", "url": SITE_URL + "/", "name": SITE_NAME,
         "publisher": {"@id": SITE_URL + "/#org"}},
    ],
}, separators=(",", ":"))

PAGES.append(dict(
    path="/index.html",
    title="CJ Business Acquisitions | Buying NC Manufacturing Businesses",
    description="We acquire and operate established engineering and manufacturing businesses in North Carolina, with continuity for employees and customers.",
    jsonld=ORG_LD,
    body="""
<section class="hero" aria-labelledby="hero-title">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow">Operator-led &middot; Confidential</span>
      <h1 id="hero-title">Acquiring Established Manufacturing &amp; Engineering Businesses in North Carolina</h1>
      <p class="hero-lead">Operator-led acquisitions with continuity for the people and customers already there &mdash; preserving what makes a business work while investing in what comes next.</p>
      <div class="hero-actions">
        <a href="/submit-a-business.html" class="btn btn-light btn-lg">Submit Your Business Confidentially</a>
        <a href="/investment-criteria.html" class="btn btn-ghost-light btn-lg">View Investment Criteria</a>
      </div>
    </div>
    <aside class="hero-panel" aria-labelledby="why-title">
      <h2 id="why-title">What owners can expect</h2>
      <ul>
        <li>[[ICON:lock]]<span><b>Confidential from the first contact</b>No outreach to your employees, customers, or competitors without your permission.</span></li>
        <li>[[ICON:wrench]]<span><b>An operator, not a flipper</b>Hands-on manufacturing and engineering experience.</span></li>
        <li>[[ICON:users]]<span><b>Continuity for your team</b>Your people and customer relationships stay at the center.</span></li>
        <li>[[ICON:doc]]<span><b>Proof of funds with every LOI</b>Equity, SBA, and seller financing.</span></li>
      </ul>
    </aside>
  </div>
</section>

<section class="section-tight" aria-label="At a glance">
  <div class="container">
    <dl class="stats">
      <div class="stat"><dt>Years in manufacturing &amp; engineering</dt><dd>8+</dd></div>
      <div class="stat"><dt>Industrial manufacturers</dt><dd>3</dd></div>
      <div class="stat"><dt>Years combined M&amp;A support</dt><dd>30+</dd></div>
      <div class="stat"><dt>Target adjusted EBITDA</dt><dd>$500K&ndash;$1.5M</dd></div>
    </dl>
  </div>
</section>

<section class="section" aria-labelledby="profile-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Buyer Profile</span>
      <h2 id="profile-title">An operator's approach to acquisitions</h2>
      <p>CJ Business Acquisitions is led by Chad Johnson, a mechanical engineer and manufacturing operator with more than eight years across three industrial manufacturers. We look beyond the financial statements to the people, processes, equipment, and customer relationships that actually drive cash flow.</p>
    </div>
    <div class="grid grid-4">
      """ + card("wrench", "Operator Background", "Hands-on manufacturing and engineering experience &mdash; not a financial buyer looking for a quick resale.") + """
      """ + card("chart", "Data-Driven", "Process improvement and data analysis used to find real operational value, not just cost cutting.") + """
      """ + card("users", "Continuity First", "Preserving your employees, your customer relationships, and the reputation you built.") + """
      """ + card("handshake", "Experienced Support", "Backed by a team bringing more than 30 years of combined M&amp;A experience.") + """
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="buybox-title">
  <div class="container">
    <div class="split">
      <div class="section-head">
        <span class="eyebrow">Acquisition Buy Box</span>
        <h2 id="buybox-title">What we look for</h2>
        <p>North Carolina &middot; Lower middle market &middot; Engineering and manufacturing. If your company is close to this profile, we would still like to hear from you.</p>
        <a class="text-link" href="/investment-criteria.html">See full investment criteria [[ICON:arrow-right]]</a>
      </div>
      <div class="panel">
        """ + criteria([
            ("Adjusted EBITDA", "$500K &ndash; $1.5M"),
            ("EBITDA margin", "15% minimum"),
            ("Operating history", "5+ years"),
            ("Customer concentration", "20% maximum"),
            ("Geography", "North Carolina"),
            ("Transition", "6 to 12 months"),
            ("Debt service coverage ratio", "1.5x+"),
            ("Cash in business at close", "1.86x equity injection"),
        ]) + """
      </div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="situations-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Owner Situations</span>
      <h2 id="situations-title">Situations we understand</h2>
      <p>Every situation is different, but these are the circumstances we most often work with.</p>
    </div>
    <div class="grid grid-3">
      """ + card("clock", "Retiring Owner", "You have built something valuable, there is no internal successor, and you want a smooth transition for the team and customers you care about.") + """
      """ + card("users", "Second-Generation Exit", "The next generation is ready to pursue a different path, and the business needs ownership prepared to carry it forward.") + """
      """ + card("layers", "Corporate or PE Carve-Out", "A non-core division or portfolio company that would benefit from focused, independent, hands-on ownership.") + """
    </div>
  </div>
</section>
""" + cta("Thinking about your next chapter?", "Whether you are an owner, a broker, or an intermediary, we welcome a confidential conversation."),
))

# ===========================================================================
# ABOUT
# ===========================================================================
PAGES.append(dict(
    path="/about.html",
    title="About Chad Johnson | CJ Business Acquisitions",
    description="Chad Johnson is an engineering leader and operator acquiring small to mid-sized manufacturing, engineering, and industrial services businesses.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">About Us</span>
    <h1>An engineer and operator, not a financial buyer</h1>
    <p>The businesses that create the most lasting value are the ones where operations, people, and process are taken as seriously as the balance sheet.</p>
  </div>
</section>

<section class="section" aria-labelledby="bio-title">
  <div class="container split">
    <div class="measure">
      <span class="eyebrow">Principal</span>
      <h2 id="bio-title">Chad Johnson</h2>
      <p class="lede">Chad Johnson is an engineering leader and entrepreneur focused on acquiring and growing small to mid-sized companies in manufacturing, engineering, industrial services, and related sectors.</p>
      <p>His background is rooted in manufacturing operations, engineering management, process improvement, and data-driven decision-making. Throughout his career, Chad has worked closely with engineering and production teams, suppliers, customers, and senior leadership to solve complex operational problems, improve processes, manage technical risk, and strengthen business performance.</p>
      <p>Chad brings an operator's perspective to business acquisitions. When evaluating a company, he looks beyond the financial statements to understand the people, processes, customers, equipment, competitive position, and operational systems that ultimately drive cash flow and long-term value.</p>
      <p>His approach is focused on acquiring established, profitable businesses with durable customer demand and room to improve. He is particularly drawn to companies where stronger operations, better use of data, technology, and automation can create meaningful value.</p>
      <p>With the support of a team bringing more than 30 years of combined M&amp;A experience, Chad's long-term strategy is to build a portfolio of complementary businesses through acquisition, organic growth, and operational improvement &mdash; preserving what already makes a business successful while adding the systems and resources for its next stage of growth.</p>
    </div>
    <aside class="profile" aria-label="Profile summary">
      <div class="profile-top">
        <div class="avatar" aria-hidden="true">CJ</div>
        <div><h3>Chad Johnson</h3><p>Principal</p></div>
      </div>
      <dl>
        <div><dt>Experience</dt><dd>8+ years, manufacturing &amp; engineering</dd></div>
        <div><dt>Prior companies</dt><dd>PRESS GLASS &middot; Weiss Technik &middot; Valco Melton</dd></div>
        <div><dt>Education</dt><dd>B.S. Mechanical Engineering Technology, University of Cincinnati</dd></div>
        <div><dt>Focus</dt><dd>Process improvement &amp; data-driven operations</dd></div>
        <div><dt>Deal support</dt><dd>30+ years combined M&amp;A experience</dd></div>
        <div><dt>Connect</dt><dd><a href="https://www.linkedin.com/in/chad-johnson-782990149" rel="noopener noreferrer" target="_blank">LinkedIn profile<span class="visually-hidden"> (opens in a new tab)</span></a></dd></div>
      </dl>
    </aside>
  </div>
</section>

<section class="section section-alt" aria-labelledby="cap-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Core Capabilities</span>
      <h2 id="cap-title">What Chad brings to every business</h2>
      <p>What Chad brings to every business he acquires and operates.</p>
    </div>
    <div class="grid grid-4">
      """ + card("gauge", "Process Improvement", "Identifying and removing waste, bottlenecks, and inefficiency on the production floor.") + """
      """ + card("compass", "Systems Thinking", "Root-cause problem solving that addresses the source of operational issues, not the symptoms.") + """
      """ + card("factory", "Manufacturing Engineering", "Hands-on knowledge of production equipment, machinery, and manufacturing processes.") + """
      """ + card("chart", "Data Analysis", "Using production and business data to guide decisions and surface opportunities.") + """
    </div>
  </div>
</section>

<section class="section" aria-labelledby="phil-title">
  <div class="container measure">
    <span class="eyebrow">Our Philosophy</span>
    <h2 id="phil-title">Continuity, then growth</h2>
    <blockquote class="quote"><p>Preserving what already makes a business successful, while adding the systems and resources for its next stage of growth.</p></blockquote>
    <p class="note">Our long-term strategy is to build a portfolio of complementary engineering and manufacturing businesses in North Carolina through acquisition, organic growth, and steady operational improvement &mdash; measured in decades, not in exit windows.</p>
  </div>
</section>
""" + cta("Let's talk about your business", "If you own, represent, or know of a business that might be a fit, we welcome a confidential conversation."),
))

# ===========================================================================
# INVESTMENT CRITERIA
# ===========================================================================
PAGES.append(dict(
    path="/investment-criteria.html",
    title="Investment Criteria | CJ Business Acquisitions",
    description="Our buy box: $500K-$1.5M adjusted EBITDA, 1.5x+ debt service coverage, 15% minimum margin, 5+ years history, North Carolina engineering and manufacturing.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Acquisition Buy Box</span>
    <h1>What we look for in a business</h1>
    <p>North Carolina &middot; Lower middle market &middot; Durable cash flow</p>
  </div>
</section>

<section class="section" aria-labelledby="fin-title">
  <div class="container split">
    <div class="section-head">
      <h2 id="fin-title">Financial &amp; operating criteria</h2>
      <p>If your company generally fits this profile, or is close, we would welcome hearing from you.</p>
    </div>
    <div class="panel">
      """ + criteria([
          ("Adjusted EBITDA", "$500,000 &ndash; $1,500,000"),
          ("Debt service coverage ratio", "1.5x+"),
          ("Cash in business at close", "1.86x equity injection"),
          ("EBITDA margin", "15% minimum"),
          ("Operating history", "5+ years"),
          ("Customer concentration", "20% maximum"),
          ("Geography", "North Carolina"),
          ("Sectors", "Engineering &amp; manufacturing"),
          ("Financial profile", "Clean reporting, reliable cash flow"),
          ("Transition", "6 to 12 months preferred"),
      ]) + """
      <p class="note"><strong>Cash in business at close:</strong> cash on the balance sheet at close of at least 1.86&times; the equity cash injection.</p>
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="sectors-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Sectors of Focus</span>
      <h2 id="sectors-title">Industries we target</h2>
      <p>Engineering and manufacturing industries, plus the businesses that serve them.</p>
    </div>
    <div class="grid grid-4">
      """ + card("factory", "Manufacturing", "Precision, industrial, and process manufacturers with established operations and repeat customers.") + """
      """ + card("wrench", "Engineering", "Engineering services and technical firms supporting industrial and commercial clients.") + """
      """ + card("gauge", "Industrial Services", "Services businesses supporting manufacturers and industrial customers.") + """
      """ + card("layers", "Related B2B", "Complementary B2B businesses that serve manufacturing or engineering companies.") + """
    </div>
  </div>
</section>

<section class="section" aria-labelledby="own-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Owner Situations</span>
      <h2 id="own-title">Where an operator-led buyer fits</h2>
      <p>The circumstances where an operator-led buyer tends to be the right fit.</p>
    </div>
    <div class="grid grid-3">
      """ + card("clock", "Retiring Owner", "No internal successor in place, and a priority on a respectful transition for employees and customers.", "01") + """
      """ + card("users", "Second-Generation Exit", "A family business where the next generation is ready to pursue a different path.", "02") + """
      """ + card("layers", "Corporate or PE Carve-Out", "A non-core division or portfolio company that deserves focused, independent ownership.", "03") + """
    </div>
  </div>
</section>
""" + cta("Is your business a fit?", "Proprietary and off-market opportunities are especially welcome. Every situation is unique."),
))

# ===========================================================================
# FOR BUSINESS OWNERS (includes the buying process)
# ===========================================================================
PHASE1 = timeline([
    ("Origination", "Find the opportunity."),
    ("Vetting", "Is this worth pursuing?"),
    ("Valuation", "What is it actually worth?"),
    ("Seller Dynamics", "What matters to them?"),
    ("Negotiation", "Can the deal work for both sides?"),
    ("LOI", "Put the right deal on paper."),
])
PHASE2 = timeline([
    ("Diligence", "Verify the business."),
    ("Financing", "Match the right capital."),
    ("Structure", "Build the transaction correctly."),
    ("Legal", "Paper the deal."),
    ("Closing", "Coordinate the final pieces."),
    ("Ownership", "Take control of the business."),
])

PAGES.append(dict(
    path="/for-business-owners.html",
    title="For Business Owners | CJ Business Acquisitions",
    description="What owners and brokers can expect: our commitments, a two-phase buying process from origination to closing, and how we finance acquisitions.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">For Owners &amp; Brokers</span>
    <h1>What you can expect working with us</h1>
    <p>Selling a business you built is personal. Here is how we work with owners, how our buying process runs from first conversation to ownership, and how we finance the deal.</p>
  </div>
</section>

<section class="section" aria-labelledby="commit-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Our Commitments</span>
      <h2 id="commit-title">How we work with owners</h2>
      <p>How we work with every owner who reaches out, whether or not a transaction ever happens.</p>
    </div>
    <div class="grid grid-3">
      """ + card("lock", "Confidentiality First", "Every conversation and submission is treated as strictly confidential. We do not contact your employees, customers, or competitors without your permission.") + """
      """ + card("wrench", "Operator's Perspective", "We evaluate your business the way an operator would &mdash; understanding your people, processes, and equipment, not just your financial statements.") + """
      """ + card("users", "Continuity for Your Team", "We aim to preserve what already works: your employees, your customer relationships, and the reputation you spent years building.") + """
    </div>
  </div>
</section>

<section class="section section-alt" id="buying-process" aria-labelledby="process-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Our Buying Process</span>
      <h2 id="process-title">From first conversation to ownership</h2>
      <p>A disciplined, two-phase process: first getting the right deal under LOI, then getting that deal to close.</p>
    </div>
    <div class="panel phase">
      <span class="phase-label">Phase 1:</span>
      <h3 class="phase-title">Getting the right<br>deal <span class="hl">under LOI</span></h3>
      """ + PHASE1 + """
    </div>
    <div class="panel phase">
      <span class="phase-label">Phase 2:</span>
      <h3 class="phase-title">Getting the deal<br><span class="hl">to close</span></h3>
      """ + PHASE2 + """
    </div>
  </div>
</section>

<section class="section" id="financing" aria-labelledby="financing-title">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Financing</span>
      <h2 id="financing-title">How we finance acquisitions</h2>
      <p class="lede">We acquire businesses using a combination of an equity injection, SBA financing, and seller financing.</p>
    </div>
    <div class="grid grid-3">
      """ + card("coins", "Equity Injection", "Buyer capital invested directly into the transaction at close.") + """
      """ + card("bank", "SBA Financing", "SBA-backed acquisition financing through an established lender.") + """
      """ + card("handshake", "Seller Financing", "A seller note that keeps both sides aligned through the transition.") + """
    </div>
    <div class="callout">
      [[ICON:doc]]
      <div>
        <h3>Proof of funds with every LOI</h3>
        <p>Once we have reviewed the business and financials, we are happy to provide proof of funds with any LOI we submit to demonstrate our ability to finance the transaction.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="advisors-title">
  <div class="container split">
    <div>
      <span class="eyebrow">Brokers &amp; Intermediaries</span>
      <h2 id="advisors-title">Working with advisors</h2>
      <p class="lede">We welcome hearing from business brokers, M&amp;A advisors, and other intermediaries representing sellers in North Carolina's engineering and manufacturing sectors.</p>
      <ul class="check-list">
        <li>[[ICON:check]]<span>We move efficiently and communicate directly</span></li>
        <li>[[ICON:check]]<span>We respect the confidentiality your clients expect</span></li>
        <li>[[ICON:check]]<span>We give a clear yes or no rather than leaving deals open-ended</span></li>
        <li>[[ICON:check]]<span>Proprietary and off-market opportunities are welcome</span></li>
      </ul>
    </div>
    <div class="panel">
      <h3>Have a client to discuss?</h3>
      <p>Send the details through our confidential form and we will respond promptly with a clear read on fit.</p>
      <a href="/submit-a-business.html" class="btn btn-block">Submit a Business</a>
    </div>
  </div>
</section>
""" + cta("Ready to start a confidential conversation?", "We respond promptly and discreetly to every inquiry."),
))

# ===========================================================================
# SUBMIT A BUSINESS
# ===========================================================================
SUBMIT_FORM = form_open("New Business Submission - CJ Business Acquisitions") + """
  <div class="form-grid">
    """ + field("contact_name", "Your name", "Contact Name", required=True, maxlength=100, autocomplete="name", data_label="your name") + """
    """ + field("role", "You are a", "Submitter Role", kind="select", options=["Business Owner", "Broker / M&amp;A Advisor", "Other Intermediary"], data_label="your role") + """
    """ + field("email", "Email address", "email", type_="email", required=True, maxlength=254, autocomplete="email", data_label="email address") + """
    """ + field("phone", "Phone number", "Phone Number", type_="tel", maxlength=25, autocomplete="tel", pattern=PHONE_PATTERN, data_label="phone number") + """
    """ + field("company", "Company name", "Company Name", required=True, maxlength=150, autocomplete="organization", data_label="the company name") + """
    """ + field("industry", "Industry", "Industry", required=True, maxlength=120, placeholder="e.g. Precision machining", data_label="the industry") + """
    """ + field("location", "Company location", "Company Location", required=True, maxlength=120, placeholder="City, state", data_label="the company location", full=True) + """
    """ + field("revenue", "Annual revenue", "Annual Revenue", maxlength=40, placeholder="e.g. $4.5M", data_label="annual revenue", opt_note="(optional, a range is fine)") + """
    """ + field("ebitda", "EBITDA / owner earnings", "EBITDA or Owner Earnings", maxlength=40, placeholder="e.g. $900K", data_label="EBITDA or owner earnings", opt_note="(optional, a range is fine)") + """
    """ + field("asking", "Asking price", "Asking Price", maxlength=40, data_label="asking price", opt_note="(if applicable)", full=True) + """
    """ + field("description", "Brief description of the business", "Business Description", kind="textarea", required=True, maxlength=3000, minlength=20, placeholder="What does the company do, how long has it operated, and what makes it valuable?", data_label="a brief description", full=True) + """
    """ + field("reason", "Reason for selling", "Reason for Selling", kind="textarea", maxlength=2000, data_label="the reason for selling", full=True) + """
    """ + field("comments", "Additional comments", "Additional Comments", kind="textarea", maxlength=2000, data_label="additional comments", full=True) + """
  </div>
""" + form_close("Submit Confidentially", 'By submitting, you agree to be contacted about this opportunity. We never share your information with third parties. See our <a href="/privacy.html">Privacy Policy</a>.')

PAGES.append(dict(
    path="/submit-a-business.html",
    title="Submit a Business | CJ Business Acquisitions",
    description="Confidentially submit a business acquisition opportunity to CJ Business Acquisitions. All inquiries are held in strict confidence.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Confidential Submission</span>
    <h1>Submit a business opportunity</h1>
    <p>Whether you are an owner, a broker, or another intermediary, share a few details and we will follow up promptly and discreetly.</p>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="panel">
      <h2 class="visually-hidden">Submission form</h2>
      <div class="callout callout-info callout-top">
        [[ICON:lock]]
        <div>
          <h3>Your information is confidential</h3>
          <p>This form is delivered directly and privately to our team. We do not share submissions with third parties, and we will not contact employees, customers, or competitors without your permission.</p>
        </div>
      </div>
      """ + SUBMIT_FORM + """
      <div id="form-success" class="form-success" role="status" hidden>
        <div class="success-icon">[[ICON:check-circle]]</div>
        <h2>Thank you. Your submission was received.</h2>
        <p>We review every submission personally and will be in touch shortly. If it is time-sensitive, email <a href="mailto:cjohnson@cjbusinessacquisitions.com">cjohnson@cjbusinessacquisitions.com</a>.</p>
        <a href="/" class="btn btn-secondary">Back to home</a>
      </div>
    </div>
    <div class="aside-stack">
      <div class="panel">
        <h2>What happens next</h2>
        <ol class="steps-mini">
          <li><span><b>We review your submission</b>Nothing is shared outside our team.</span></li>
          <li><span><b>An introductory call</b>We learn about your business, goals, and timeline, and answer your questions about us.</span></li>
          <li><span><b>NDA before details</b>If there is a fit, we sign a non-disclosure agreement before any detailed financials are exchanged.</span></li>
        </ol>
      </div>
      <div class="alert alert-info">[[ICON:shield]]<p><strong>Please do not attach or paste confidential financial statements here.</strong> Approximate figures are enough for a first look.</p></div>
    </div>
  </div>
</section>
""",
))

# ===========================================================================
# CONTACT
# ===========================================================================
CONTACT_FORM = form_open("New Contact Form Message - CJ Business Acquisitions") + """
  <div class="form-grid">
    """ + field("cname", "Full name", "Full Name", required=True, maxlength=100, autocomplete="name", data_label="your name") + """
    """ + field("cemail", "Email address", "email", type_="email", required=True, maxlength=254, autocomplete="email", data_label="email address") + """
    """ + field("cphone", "Phone", "Phone Number", type_="tel", maxlength=25, autocomplete="tel", pattern=PHONE_PATTERN, data_label="phone number") + """
    """ + field("cinterest", "Reaching out about", "Inquiry Type", kind="select", required=True, options=["Selling My Business", "Representing a Business Owner", "General Inquiry", "Other"], data_label="what you are reaching out about") + """
    """ + field("cmessage", "Message", "Message", kind="textarea", required=True, maxlength=3000, minlength=10, data_label="a message", full=True) + """
  </div>
""" + form_close("Send Message", 'We use your details only to respond to you. See our <a href="/privacy.html">Privacy Policy</a>.')

PAGES.append(dict(
    path="/contact.html",
    title="Contact | CJ Business Acquisitions",
    description="Contact CJ Business Acquisitions about an acquisition opportunity in North Carolina's engineering and manufacturing sectors.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Contact</span>
    <h1>Let's start a conversation</h1>
    <p>Have a question, a business to discuss, or simply want to introduce yourself? We respond promptly to every inquiry.</p>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="panel">
      <h2 class="visually-hidden">Contact form</h2>
      """ + CONTACT_FORM + """
      <div id="form-success" class="form-success" role="status" hidden>
        <div class="success-icon">[[ICON:check-circle]]</div>
        <h2>Thank you. Your message was sent.</h2>
        <p>We will be in touch shortly.</p>
        <a href="/" class="btn btn-secondary">Back to home</a>
      </div>
    </div>
    <div class="aside-stack">
      <div class="panel">
        <span class="eyebrow">Direct Contact</span>
        <h2>Reach us directly</h2>
        <p>Prefer to skip the form? Contact Chad directly. All inquiries are held in strict confidence, and an NDA is available on request.</p>
        <ul class="contact-list">
          <li>[[ICON:mail]]<a href="mailto:cjohnson@cjbusinessacquisitions.com">cjohnson@cjbusinessacquisitions.com</a></li>
          <li>[[ICON:phone]]<a href="tel:+17402381005">740-238-1005</a></li>
          <li>[[ICON:linkedin]]<a href="https://www.linkedin.com/in/chad-johnson-782990149" rel="noopener noreferrer" target="_blank">LinkedIn profile<span class="visually-hidden"> (opens in a new tab)</span></a></li>
          <li>[[ICON:pin]]<span>North Carolina</span></li>
        </ul>
      </div>
      <div class="panel">
        <h2>Have a specific business?</h2>
        <p>Use our confidential submission form to share the details and get a prompt read on fit.</p>
        <a href="/submit-a-business.html" class="btn btn-block">Submit a Business</a>
      </div>
    </div>
  </div>
</section>
""",
))

# ===========================================================================
# PRIVACY POLICY
# ===========================================================================
PAGES.append(dict(
    path="/privacy.html",
    title="Privacy Policy | CJ Business Acquisitions",
    description="How CJ Business Acquisitions collects, uses, and protects information submitted through this website.",
    body="""
<section class="page-hero">
  <div class="container">
    <span class="eyebrow">Legal</span>
    <h1>Privacy Policy</h1>
    <p>Last updated September 25, 2026</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="prose">
      <h2>Who we are</h2>
      <p>This website is operated by CJ Business Acquisitions (&ldquo;we,&rdquo; &ldquo;us&rdquo;), which acquires and operates engineering and manufacturing businesses in North Carolina. Questions about this policy can be sent to <a href="mailto:cjohnson@cjbusinessacquisitions.com">cjohnson@cjbusinessacquisitions.com</a>.</p>

      <h2>Information we collect</h2>
      <p>We only collect information you choose to send us:</p>
      <ul>
        <li><strong>Submit a Business form:</strong> your name, role, email, phone number, company name, location, industry, and any financial figures, descriptions, or comments you provide.</li>
        <li><strong>Contact form:</strong> your name, email, phone number, inquiry type, and message.</li>
        <li><strong>Email and phone:</strong> anything you send us directly.</li>
      </ul>
      <p>Please do not send confidential financial statements through the website. If there is a mutual fit, we will ask for detailed information under a non-disclosure agreement.</p>

      <h2>Information collected automatically</h2>
      <p>We do not use analytics, advertising trackers, or tracking cookies. Our hosting provider records standard technical logs (such as IP address, browser type, and pages requested) to operate and secure the site. If you choose a light or dark theme, that preference is stored only in your own browser.</p>
      <p>To block spam, our forms use hCaptcha, a verification service that may process technical information about your device and interaction and may set cookies needed for that check. hCaptcha only loads once you start filling in a form.</p>

      <h2>How we use your information</h2>
      <ul>
        <li>To respond to your inquiry and evaluate a potential acquisition opportunity.</li>
        <li>To communicate with you about that opportunity.</li>
        <li>To protect the website and our forms against spam and abuse.</li>
      </ul>
      <p>We do not sell or rent your information, and we do not use it for unrelated marketing.</p>

      <h2>Service providers</h2>
      <p>We use a small number of providers to run this website. Each processes information only as needed to provide its service:</p>
      <ul>
        <li><strong>Vercel</strong> &ndash; website hosting.</li>
        <li><strong>Cloudflare</strong> &ndash; domain name services.</li>
        <li><strong>Web3Forms</strong> &ndash; delivers form submissions to our email inbox.</li>
        <li><strong>hCaptcha</strong> &ndash; spam and bot protection on our forms.</li>
        <li><strong>Google Workspace</strong> &ndash; our business email.</li>
      </ul>

      <h2>Confidentiality and retention</h2>
      <p>We treat every submission as confidential and limit access to our team and professional advisors who are bound by confidentiality obligations. We keep submissions only as long as needed to evaluate and pursue an opportunity, or as required for legal or record-keeping reasons. Our form delivery provider may keep a copy of submissions for a limited period under its own policy.</p>

      <h2>Your choices</h2>
      <p>You can ask us to access, correct, or delete the information you have sent us by emailing <a href="mailto:cjohnson@cjbusinessacquisitions.com">cjohnson@cjbusinessacquisitions.com</a>. We will respond within a reasonable time.</p>

      <h2>Security</h2>
      <p>This website is served only over encrypted HTTPS connections and uses modern browser security protections. No method of transmission over the internet is completely secure, so please share only the information needed for an initial conversation.</p>

      <h2>Children</h2>
      <p>This website is intended for business owners and professionals and is not directed to children under 13.</p>

      <h2>Changes to this policy</h2>
      <p>We may update this policy from time to time. The date at the top of this page shows when it was last changed.</p>
    </div>
  </div>
</section>
""",
))

# ===========================================================================
# 404
# ===========================================================================
PAGES.append(dict(
    path="/404.html",
    title="Page Not Found | CJ Business Acquisitions",
    description="The page you requested could not be found.",
    noindex=True,
    body="""
<section class="section notfound">
  <div class="container">
    <p class="code">ERROR 404</p>
    <h1>We could not find that page</h1>
    <p class="lede">The link may be out of date, or the address may have a typo.</p>
    <div class="actions">
      <a href="/" class="btn btn-lg">Go to the homepage</a>
      <a href="/submit-a-business.html" class="btn btn-secondary btn-lg">Submit a Business</a>
      <a href="/contact.html" class="btn btn-secondary btn-lg">Contact Us</a>
    </div>
  </div>
</section>
""",
))
