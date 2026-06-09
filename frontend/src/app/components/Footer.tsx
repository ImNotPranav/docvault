import { Shield, Lock } from "lucide-react";

const footerLinks = {
    Product: ["Features", "How It Works", "Privacy"],
    Resources: ["Setup Guide", "Documentation"],
    Legal: ["Privacy Policy", "Terms"],
};

export default function Footer() {
    return (
        <footer className="border-t border-white/10 bg-[#0a0a1a]/60 backdrop-blur-sm mt-auto">
            <div className="max-w-7xl mx-auto px-6 py-12">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="col-span-2 md:col-span-1">
                        <div className="flex items-center gap-2.5 mb-4">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                                <Shield className="w-4 h-4 text-white" />
                            </div>
                            <span className="text-base font-semibold text-white">DocVault</span>
                        </div>
                        <p className="text-sm text-slate-500 leading-relaxed">
                            Privacy-first document analysis. All processing happens locally on your device.
                        </p>
                        <div className="flex items-center gap-1.5 mt-3">
                            <Lock className="w-3 h-3 text-emerald-500" />
                            <span className="text-xs text-emerald-400/80">No cloud. No tracking. Your data stays yours.</span>
                        </div>
                    </div>

                    {/* Link Columns */}
                    {Object.entries(footerLinks).map(([category, links]) => (
                        <div key={category}>
                            <h4 className="text-sm font-semibold text-slate-300 mb-4">{category}</h4>
                            <ul className="space-y-3">
                                {links.map((link) => (
                                    <li key={link}>
                                        <a
                                            href="#"
                                            className="text-sm text-slate-500 hover:text-white transition-colors"
                                        >
                                            {link}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Bottom bar */}
                <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-xs text-slate-600">
                        © {new Date().getFullYear()} DocVault. All rights reserved.
                    </p>
                    <p className="text-xs text-slate-600">
                        Powered by Gemma 3 via Ollama — 100% local inference.
                    </p>
                </div>
            </div>
        </footer>
    );
}
