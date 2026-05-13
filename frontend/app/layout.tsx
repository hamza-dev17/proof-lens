export const metadata = {
  title: "ProofLens",
  description: "Turkish-first misinformation verification dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
