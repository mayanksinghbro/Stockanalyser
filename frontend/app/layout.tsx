import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "NSE Antigravity Predictor",
    description: "Advanced ML Stock Prediction Engine for NSE",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
