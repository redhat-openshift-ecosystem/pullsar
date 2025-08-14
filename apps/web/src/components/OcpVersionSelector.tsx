import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'

interface Props {
  versions: string[]
  currentVersion: string
  onVersionChange: (version: string) => void
}

export function OcpVersionSelector({
  versions,
  currentVersion,
  onVersionChange,
}: Props) {
  return (
    <div>
      <label className="block text-sm font-medium text-secondary mb-1">
        OCP Version
      </label>
      <Select value={currentVersion} onValueChange={onVersionChange}>
        <SelectTrigger className="justify-start text-left font-normal bg-input border-border">
          <SelectValue placeholder="Select a version" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {versions.map((version) => (
              <SelectItem key={version} value={version}>
                {version}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  )
}
